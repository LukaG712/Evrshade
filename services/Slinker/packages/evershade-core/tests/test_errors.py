"""Tests for evershade.errors — Error handling and middleware."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from evershade.errors import (
    ErrorCode,
    EvershadeError,
    error_response,
    success_response,
    register_error_handlers,
    CorrelationIdMiddleware,
    RequestLoggingMiddleware,
    ERROR_CODE_TO_STATUS,
)


class TestErrorCode:
    """Test ErrorCode enum."""

    def test_all_codes_have_status(self):
        """Every error code maps to an HTTP status."""
        for code in ErrorCode:
            assert code in ERROR_CODE_TO_STATUS
            assert 400 <= ERROR_CODE_TO_STATUS[code] <= 599

    def test_validation_error_is_400(self):
        assert ERROR_CODE_TO_STATUS[ErrorCode.VALIDATION_ERROR] == 400

    def test_not_found_is_404(self):
        assert ERROR_CODE_TO_STATUS[ErrorCode.NOT_FOUND] == 404

    def test_internal_error_is_500(self):
        assert ERROR_CODE_TO_STATUS[ErrorCode.INTERNAL_ERROR] == 500


class TestEvershadeError:
    """Test EvershadeError exception."""

    def test_error_message(self):
        err = EvershadeError(ErrorCode.NOT_FOUND, "Agent not found")
        assert err.code == ErrorCode.NOT_FOUND
        assert err.message == "Agent not found"
        assert err.details is None
        assert "NOT_FOUND" in str(err)

    def test_error_with_details(self):
        err = EvershadeError(ErrorCode.VALIDATION_ERROR, "Bad input", details={"field": "name"})
        assert err.details == {"field": "name"}


class TestErrorResponse:
    """Test error/success response builders."""

    def test_error_response_format(self):
        resp = error_response(ErrorCode.NOT_FOUND, "Not found", request_id="test-123")
        assert resp["success"] is False
        assert resp["data"] is None
        assert resp["error"]["code"] == "NOT_FOUND"
        assert resp["error"]["message"] == "Not found"
        assert resp["requestId"] == "test-123"
        assert "timestamp" in resp

    def test_success_response_format(self):
        resp = success_response({"id": 1}, request_id="test-456")
        assert resp["success"] is True
        assert resp["data"] == {"id": 1}
        assert resp["error"] is None
        assert resp["requestId"] == "test-456"


class TestErrorHandlers:
    """Test global exception handlers."""

    def test_evershade_error_handler(self):
        app = FastAPI()
        register_error_handlers(app)

        @app.get("/test")
        async def test():
            raise EvershadeError(ErrorCode.NOT_FOUND, "Not found")

        with TestClient(app) as client:
            resp = client.get("/test")
            assert resp.status_code == 404
            data = resp.json()
            assert data["success"] is False
            assert data["error"]["code"] == "NOT_FOUND"

    def test_validation_error_handler(self):
        app = FastAPI()
        register_error_handlers(app)

        class ItemInput(BaseModel):
            name: str = Field(..., min_length=3)

        @app.post("/test")
        async def test(item: ItemInput):
            return item

        with TestClient(app) as client:
            resp = client.post("/test", json={"name": "ab"})
            assert resp.status_code == 400
            data = resp.json()
            assert data["success"] is False
            assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_generic_error_handler(self):
        app = FastAPI()
        register_error_handlers(app)

        @app.get("/test")
        async def test():
            raise RuntimeError("Unexpected")

        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.get("/test")
            assert resp.status_code == 500
            data = resp.json()
            assert data["success"] is False
            assert data["error"]["code"] == "INTERNAL_ERROR"


class TestCorrelationIdMiddleware:
    """Test correlation ID middleware."""

    def test_generates_request_id(self):
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        @app.get("/test")
        async def test(request: Request):
            return {"request_id": request.state.request_id}

        with TestClient(app) as client:
            resp = client.get("/test")
            assert resp.status_code == 200
            assert "X-Request-Id" in resp.headers
            assert resp.json()["request_id"] == resp.headers["X-Request-Id"]

    def test_preserves_incoming_request_id(self):
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)

        @app.get("/test")
        async def test(request: Request):
            return {"request_id": request.state.request_id}

        with TestClient(app) as client:
            resp = client.get("/test", headers={"X-Request-Id": "my-id-123"})
            assert resp.headers["X-Request-Id"] == "my-id-123"
            assert resp.json()["request_id"] == "my-id-123"


class TestRequestLoggingMiddleware:
    """Test request logging middleware."""

    def test_logs_request(self):
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/test")
        async def test():
            return {"ok": True}

        with TestClient(app) as client:
            resp = client.get("/test")
            assert resp.status_code == 200
