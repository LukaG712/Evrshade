"""Shrewd — Main application entry point.

Shrewd provides a unified interface for multiple LLM providers with model
routing, fallback, and cost tracking. It integrates with Opik for optional
LLM observability when OPIK_ENDPOINT is configured.
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

from app.database import init_db
from app.routes.management import router as management_router
from app.routes.chat import router as chat_router
from app.routing import ModelRouter

VERSION = "2.0.0"

config = ServiceConfig(service_name="Shrewd", port=8089)

# Opik integration (optional)
opik_endpoint = os.getenv("OPIK_ENDPOINT", "")

# Hider integration (optional)
hider_url = os.getenv("HIDER_URL", "")

# Langfuse integration (optional)
langfuse_client = None
try:
    from langfuse import get_langfuse_client
    langfuse_client = get_langfuse_client()
except ImportError:
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and integrations on startup."""
    await init_db()

    # Create traced HTTP client for inter-service calls
    app.state.http_client = create_traced_httpx_client()

    # Initialize model router
    app.state.model_router = ModelRouter(hider_url=hider_url)

    # Initialize Langfuse client
    global langfuse_client
    try:
        from langfuse import get_langfuse_client
        langfuse_client = get_langfuse_client()
        app.state.langfuse_enabled = langfuse_client.enabled
    except ImportError:
        app.state.langfuse_enabled = False

    yield

    # Cleanup
    await app.state.http_client.aclose()
    if langfuse_client:
        langfuse_client.flush()


app = FastAPI(
    title="Shrewd",
    description="Evershade - unified interface for multiple LLM providers with model routing",
    version=VERSION,
    lifespan=lifespan,
)

# Middleware — order matters
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Error handlers
register_error_handlers(app)

# Health and metrics endpoints
register_health_routes(app, service_name="Shrewd", version=VERSION)

# OpenTelemetry tracing
setup_telemetry(app, service_name="Shrewd")

# Register business routes
app.include_router(management_router)
app.include_router(chat_router)


@app.get("/api/capabilities")
async def capabilities():
    """Return the list of capabilities and integration status."""
    integrations = {}
    if opik_endpoint:
        integrations["opik"] = {
            "enabled": True,
            "endpoint": opik_endpoint,
        }
    else:
        integrations["opik"] = {"enabled": False}
    integrations["opentelemetry"] = {"enabled": config.telemetry.is_configured}
    integrations["langfuse"] = {
        "enabled": bool(langfuse_client and langfuse_client.enabled),
        "endpoint": langfuse_client.endpoint if langfuse_client else None,
    }
    integrations["hider"] = {
        "enabled": bool(hider_url),
        "endpoint": hider_url if hider_url else None,
    }

    return {
        "service": "Shrewd",
        "version": VERSION,
        "capabilities": [
            "providers", "models", "chat_completions",
            "usage_tracking", "routing_rules", "privacy_rules",
            "model_routing", "fallback_policies", "per_task_model_selection",
            "hider_credentials", "usage_stats",
        ],
        "integrations": integrations,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower(),
    )