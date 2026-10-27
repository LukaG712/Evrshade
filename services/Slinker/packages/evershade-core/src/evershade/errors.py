"""Standard error response envelope and middleware for Evershade services.

Every service returns errors in a consistent JSON format:
    {
      "success": false,
      "data": null,
      "error": {
        "code": "VALIDATION_ERROR",
        "message": "Human-readable description",
        "details": "Optional technical context"
      },
      "requestId": "uuid",
      "timestamp": "2026-10-26T10:00:00Z"
    }

Usage:
    from evershade.errors import error_response, EvershadeError, ErrorCode, error_middleware
    raise EvershadeError(ErrorCode.NOT_FOUND, "Agent not found", agent_id="abc")
    app.add_middleware(error_middleware)
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("evershade.errors")


class ErrorCode(str, Enum):
    """Standard error codes for Evershade services."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


ERROR_CODE_TO_STATUS = {
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
    ErrorCode.INTERNAL_ERROR: 500,
}


class EvershadeError(Exception):
    """Application-level error with structured payload.

    Args:
        code: Standard error code.
        message: Human-readable description.
        details: Optional technical context (dict or string).
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        details: Optional[Any] = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details
        super().__init__(f"{code.value}: {message}")


def error_response(
    code: ErrorCode,
    message: str,
    *,
    details: Optional[Any] = None,
    request_id: Optional[str] = None,
) -> dict[str, Any]:
    """Build a standard error response envelope."""
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code.value,
            "message": message,
            "details": details,
        },
        "requestId": request_id or str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def success_response(
    data: Any,
    *,
    request_id: Optional[str] = None,
) -> dict[str, Any]:
    """Build a standard success response envelope."""
    return {
        "success": True,
        "data": data,
        "error": None,
        "requestId": request_id or str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on a FastAPI app.

    Catches EvershadeError, RequestValidationError, and generic exceptions,
    returning a consistent JSON envelope.
    """

    @app.exception_handler(EvershadeError)
    async def evershade_error_handler(request: Request, exc: EvershadeError) -> Response:
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        body = error_response(exc.code, exc.message, details=exc.details, request_id=request_id)
        status = ERROR_CODE_TO_STATUS.get(exc.code, 500)
        return JSONResponse(status_code=status, content=body)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> Response:
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        body = error_response(
            ErrorCode.VALIDATION_ERROR,
            "Request validation failed",
            details=exc.errors(),
            request_id=request_id,
        )
        return JSONResponse(status_code=400, content=body)

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> Response:
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        logger.exception("Unhandled exception: %s", exc)
        body = error_response(
            ErrorCode.INTERNAL_ERROR,
            "An internal error occurred",
            request_id=request_id,
        )
        return JSONResponse(status_code=500, content=body)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware that generates and propagates correlation IDs.

    Every request receives a unique correlation ID stored in:
    - request.state.request_id (for access in handlers)
    - X-Request-Id response header
    - X-Correlation-Id response header (alias)

    If the incoming request contains X-Request-Id, that value is preserved.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Correlation-Id"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every request with timing and correlation ID."""

    async def dispatch(self, request: Request, call_next):
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        start = datetime.now(timezone.utc)
        try:
            response = await call_next(request)
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            logger.info(
                "req_id=%s %s %s %s %.1fms",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                duration,
            )
            return response
        except Exception:
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            logger.error(
                "req_id=%s %s %s ERROR %.1fms",
                request_id,
                request.method,
                request.url.path,
                duration,
            )
            raise
