"""Service-to-service JWT authentication.

Provides JWT token generation and validation for internal service communication.
Each service gets an identity token signed with a shared secret.

Usage:
    from evershade.auth import create_service_token, verify_service_token, auth_middleware

    # Generate token for a service
    token = create_service_token("Greenie", secret="my-secret")

    # Validate token
    payload = verify_service_token(token, secret="my-secret")
"""

from __future__ import annotations

import time
from typing import Any

import jwt
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

# Public paths that don't require authentication
PUBLIC_PATHS = {
    "/health",
    "/ready",
    "/metrics",
    "/api/status",
    "/docs",
    "/openapi.json",
}


def create_service_token(
    service_name: str,
    secret: str,
    *,
    expiry_seconds: int = 3600,
    algorithm: str = "HS256",
) -> str:
    """Create a JWT token for a service identity.

    Args:
        service_name: Name of the service.
        secret: Shared signing secret.
        expiry_seconds: Token lifetime in seconds.
        algorithm: JWT signing algorithm.

    Returns:
        Encoded JWT token string.
    """
    now = time.time()
    payload = {
        "sub": service_name,
        "iat": now,
        "exp": now + expiry_seconds,
        "type": "service",
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def verify_service_token(
    token: str,
    secret: str,
    *,
    algorithm: str = "HS256",
) -> dict[str, Any]:
    """Verify and decode a service JWT token.

    Args:
        token: JWT token string.
        secret: Shared signing secret.
        algorithm: JWT signing algorithm.

    Returns:
        Decoded payload dictionary.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid.
    """
    return jwt.decode(token, secret, algorithms=[algorithm])


class ServiceAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for validating service-to-service JWT tokens.

    Validates the Authorization: Bearer <token> header on internal API calls.
    Public paths (health, metrics, docs) are exempt from authentication.

    Args:
        secret: Shared JWT signing secret.
        public_paths: Additional paths to exempt from auth.
    """

    def __init__(
        self,
        app,
        secret: str,
        public_paths: set[str] | None = None,
    ):
        super().__init__(app)
        self.secret = secret
        self.public_paths = PUBLIC_PATHS | (public_paths or set())

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)

        # Skip auth if no secret is configured
        if not self.secret:
            return await call_next(request)

        # Extract and validate token
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"},
            )

        token = authorization[7:]
        try:
            payload = verify_service_token(token, self.secret)
            request.state.service_name = payload.get("sub", "unknown")
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail": "Token expired"})
        except jwt.InvalidTokenError as e:
            return JSONResponse(status_code=401, content={"detail": f"Invalid token: {e}"})

        return await call_next(request)


security = HTTPBearer(auto_error=False)


async def require_service_auth(
    credentials: HTTPAuthorizationCredentials | None = None,
    secret: str = "",
) -> str | None:
    """Dependency for protecting individual endpoints.

    Args:
        credentials: Bearer token from Authorization header.
        secret: Shared JWT signing secret.

    Returns:
        Service name from token payload, or None if auth is disabled.

    Raises:
        HTTPException: If authentication fails.
    """
    if not secret or not credentials:
        return None

    try:
        payload = verify_service_token(credentials.credentials, secret)
        return payload.get("sub")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
