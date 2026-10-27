"""Hider — Main application entry point.

Hider is the secrets management service for the Evershade platform. It provides:
- Encrypted secrets storage using AES-256-GCM
- Secrets CRUD operations
- Versioned configuration management
- Audit logging for all secret access
- Service-to-service authentication tokens
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from evershade.config import ServiceConfig
from evershade.errors import (
    CorrelationIdMiddleware,
    RequestLoggingMiddleware,
    register_error_handlers,
)
from evershade.health import register_health_routes
from evershade.telemetry import create_traced_httpx_client, setup_telemetry
from fastapi import FastAPI

from app.database import init_db
from app.routes import config, secrets

VERSION = "2.0.0"

config_settings = ServiceConfig(service_name="Hider", port=8087)


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

# Middleware
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
