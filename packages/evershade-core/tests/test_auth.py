"""Tests for evershade.auth — JWT authentication."""

import pytest
import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from evershade.auth import (
    create_service_token,
    verify_service_token,
    ServiceAuthMiddleware,
    PUBLIC_PATHS,
)


SECRET = "test-secret-key-12345"


class TestServiceToken:
    """Test JWT token creation and verification."""

    def test_create_and_verify(self):
        """Create and verify a service token."""
        token = create_service_token("Greenie", SECRET)
        payload = verify_service_token(token, SECRET)
        assert payload["sub"] == "Greenie"
        assert payload["type"] == "service"

    def test_wrong_secret(self):
        """Wrong secret raises InvalidTokenError."""
        token = create_service_token("Greenie", SECRET)
        with pytest.raises(jwt.InvalidTokenError):
            verify_service_token(token, "wrong-secret")

    def test_expired_token(self):
        """Expired token raises ExpiredSignatureError."""
        token = create_service_token("Greenie", SECRET, expiry_seconds=0)
        with pytest.raises(jwt.ExpiredSignatureError):
            verify_service_token(token, SECRET)

    def test_custom_expiry(self):
        """Custom expiry is respected."""
        token = create_service_token("Greenie", SECRET, expiry_seconds=7200)
        payload = verify_service_token(token, SECRET)
        assert payload["exp"] - payload["iat"] == 7200


class TestServiceAuthMiddleware:
    """Test auth middleware."""

    def setup_app(self, secret: str = ""):
        app = FastAPI()
        app.add_middleware(ServiceAuthMiddleware, secret=secret)

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        @app.get("/api/test")
        async def test():
            return {"ok": True}

        return app

    def test_public_paths_exempt(self):
        """Public paths don't require auth."""
        app = self.setup_app(secret=SECRET)
        with TestClient(app) as client:
            resp = client.get("/health")
            assert resp.status_code == 200

    def test_no_secret_allows_all(self):
        """No secret means auth is disabled."""
        app = self.setup_app(secret="")
        with TestClient(app) as client:
            resp = client.get("/api/test")
            assert resp.status_code == 200

    def test_valid_token(self):
        """Valid token allows access."""
        app = self.setup_app(secret=SECRET)
        token = create_service_token("Slinker", SECRET)
        with TestClient(app) as client:
            resp = client.get("/api/test", headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code == 200

    def test_missing_token(self):
        """Missing token returns 401."""
        app = self.setup_app(secret=SECRET)
        with TestClient(app) as client:
            resp = client.get("/api/test")
            assert resp.status_code == 401

    def test_invalid_token(self):
        """Invalid token returns 401."""
        app = self.setup_app(secret=SECRET)
        with TestClient(app) as client:
            resp = client.get("/api/test", headers={"Authorization": "Bearer invalid"})
            assert resp.status_code == 401


class TestPublicPaths:
    """Test public paths list."""

    def test_health_is_public(self):
        assert "/health" in PUBLIC_PATHS

    def test_metrics_is_public(self):
        assert "/metrics" in PUBLIC_PATHS

    def test_docs_is_public(self):
        assert "/docs" in PUBLIC_PATHS
