"""Evershade Core — Security middleware.

Provides CORS configuration and rate limiting for all Evershade services.
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


def add_cors_middleware(
    app: ASGIApp,
    allowed_origins: list[str] | None = None,
    allowed_methods: list[str] | None = None,
    allowed_headers: list[str] | None = None,
) -> None:
    """Add CORS middleware to a FastAPI app.

    Args:
        app: The FastAPI application.
        allowed_origins: List of allowed origins. Defaults to all origins.
        allowed_methods: List of allowed HTTP methods.
        allowed_headers: List of allowed HTTP headers.
    """
    from starlette.middleware.cors import CORSMiddleware

    if allowed_origins is None:
        allowed_origins = ["*"]
    if allowed_methods is None:
        allowed_methods = ["*"]
    if allowed_headers is None:
        allowed_headers = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
    )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware.

    Limits requests per IP address. Public paths (health, metrics, docs)
    are exempt from rate limiting.

    Args:
        app: The ASGI application.
        requests_per_minute: Maximum requests per minute per IP.
        public_paths: Paths to exempt from rate limiting.
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        public_paths: set[str] | None = None,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.public_paths = public_paths or {
            "/health",
            "/ready",
            "/metrics",
            "/api/status",
            "/docs",
            "/openapi.json",
        }
        # Store: {ip: [(timestamp, ...)]}
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._window = 60  # 60 second window

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check X-Forwarded-For header first (for reverse proxy setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if a client IP is rate limited."""
        now = time.time()
        window_start = now - self._window

        # Clean old entries
        self._requests[client_ip] = [ts for ts in self._requests[client_ip] if ts > window_start]

        # Check limit
        return len(self._requests[client_ip]) >= self.requests_per_minute

    def _record_request(self, client_ip: str) -> None:
        """Record a request from a client IP."""
        self._requests[client_ip].append(time.time())

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        if self._is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Try again later.",
                    "retry_after": 60,
                },
                headers={"Retry-After": "60"},
            )

        self._record_request(client_ip)
        response = await call_next(request)
        return response


def add_security_middleware(
    app: ASGIApp,
    requests_per_minute: int = 60,
    allowed_origins: list[str] | None = None,
) -> None:
    """Add both CORS and rate limiting middleware to a FastAPI app.

    Convenience function that adds both security middlewares at once.

    Args:
        app: The FastAPI application.
        requests_per_minute: Maximum requests per minute per IP.
        allowed_origins: List of allowed CORS origins.
    """
    add_cors_middleware(app, allowed_origins=allowed_origins)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute)
