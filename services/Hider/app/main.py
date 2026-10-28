"""Hider — Main application entry point.

Hider is the secrets management service for the Evershade platform. It provides:
- Encrypted secrets storage using AES-256-GCM
- Secrets CRUD operations
- Versioned configuration management
- Audit logging for all secret access
- Service-to-service authentication tokens
"""

from __future__ import annotations

import hmac
import os
from contextlib import asynccontextmanager

from evershade.config import ServiceConfig
from evershade.errors import (
    CorrelationIdMiddleware,
    RequestLoggingMiddleware,
    register_error_handlers,
)
from evershade.health import register_health_routes
from evershade.security import add_security_middleware
from evershade.telemetry import create_traced_httpx_client, setup_telemetry
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routes import config, secrets

VERSION = "2.0.0"

config_settings = ServiceConfig(service_name="Hider", port=8087)

# API key authentication — required, service refuses to start without it
API_KEY = os.getenv("API_KEY", "")
if not API_KEY:
    raise RuntimeError(
        "API_KEY environment variable is not set. Refusing to start Hider without a configured API key. "
        "Generate one: openssl rand -hex 32"
    )

PUBLIC_PATHS = {
    "/health",
    "/ready",
    "/metrics",
    "/api/status",
    "/docs",
    "/openapi.json",
}


async def auth_middleware(request: Request, call_next):
    """Authenticate requests using API key."""
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing or invalid Authorization header"},
        )
    token = authorization[7:]
    if not hmac.compare_digest(token, API_KEY):
        return JSONResponse(status_code=401, content={"detail": "Invalid API key"})

    return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    await init_db()
    app.state.http_client = create_traced_httpx_client()
    yield
    await app.state.http_client.aclose()


app = FastAPI(
    title="Hider",
    description="Evershade secrets management and encryption service",
    version=VERSION,
    lifespan=lifespan,
)

# Security middleware
add_security_middleware(app, requests_per_minute=60)

# Authentication middleware
app.add_middleware(auth_middleware)

# Other middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Error handlers
register_error_handlers(app)

# Health and metrics endpoints
register_health_routes(app, service_name="Hider", version=VERSION)

# OpenTelemetry tracing
setup_telemetry(app, service_name="Hider")

# API routes
app.include_router(secrets.router, prefix="/api/secrets", tags=["secrets"])
app.include_router(config.router, prefix="/api/config", tags=["config"])


@app.get("/api/capabilities")
async def capabilities():
    """Return the list of capabilities and integration status."""
    return {
        "service": "Hider",
        "version": VERSION,
        "capabilities": [
            "secrets_encryption",
            "secrets_storage",
            "versioned_config",
            "audit_logging",
            "service_tokens",
            "aes_256_gcm",
        ],
        "integrations": {
            "opentelemetry": {"enabled": config_settings.telemetry.is_configured},
            "sqlite": {
                "enabled": True,
                "path": os.getenv("DB_PATH", "/app/data/hider.db"),
            },
            "encryption": {
                "enabled": bool(os.getenv("ENCRYPTION_KEY")),
                "algorithm": "AES-256-GCM",
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=config_settings.host,
        port=config_settings.port,
        log_level=config_settings.log_level.lower(),
    )
