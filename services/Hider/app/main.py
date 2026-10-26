"""Hider — Main application entry point.

Hider is the secrets and configuration service for the Evershade platform. It provides:
- AES-256-GCM encrypted secret storage
- Versioned configuration management
- Secret access audit logging
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from evershade.config import ServiceConfig
from evershade.errors import (
    CorrelationIdMiddleware,
    RequestLoggingMiddleware,
    register_error_handlers,
)
from evershade.health import register_health_routes
from evershade.telemetry import setup_telemetry, create_traced_httpx_client

from app.database import init_db, db
from app.routes import secrets, config, security
from app.security import SecurityManager

VERSION = "2.0.0"

config_obj = ServiceConfig(service_name="Hider", port=8087)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    await init_db()

    # Create traced HTTP client for inter-service calls
    app.state.http_client = create_traced_httpx_client()

    # Initialize security manager
    app.state.security_manager = SecurityManager(db, app.state.http_client)

    yield

    # Cleanup
    await app.state.http_client.aclose()


app = FastAPI(
    title="Hider",
    description="Evershade - encrypted storage and retrieval of secrets and centralized configuration",
    version=VERSION,
    lifespan=lifespan,
)

# Middleware — order matters
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Error handlers
register_error_handlers(app)

# Health and metrics endpoints
register_health_routes(app, service_name="Hider", version=VERSION)

# OpenTelemetry tracing
setup_telemetry(app, service_name="Hider")

# API routes
app.include_router(secrets.router)
app.include_router(config.router)
app.include_router(security.router)


@app.get("/api/capabilities")
async def capabilities():
    """Return the list of capabilities and integration status."""
    return {
        "service": "Hider",
        "version": VERSION,
        "capabilities": [
            "encrypted_secrets",
            "versioned_config",
            "audit_log",
            "config_history",
            "agent_permissions",
            "service_tokens",
            "security_audit",
            "ssrf_protection",
            "content_safety",
        ],
        "integrations": {
            "opentelemetry": {"enabled": config_obj.telemetry.is_configured},
            "sqlite": {"enabled": True, "path": os.getenv("HIDER_DB_PATH", "/data/hider.db")},
            "encryption": {"algorithm": "AES-256-GCM"},
            "security_manager": {"enabled": True},
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config_obj.host,
        port=config_obj.port,
        log_level=config_obj.log_level.lower(),
    )