"""Greenie — Main application entry point.

Greenie is the central agent orchestration service for the Evershade platform. It provides:
- Agent lifecycle management (create, update, delete agents)
- Mission planning and execution
- Task delegation to Slinker (code execution)
- Chat sessions with agents
- Service registry and discovery
- SSE/WebSocket streaming for real-time updates
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
from evershade.registry import ServiceRegistry
from evershade.telemetry import setup_telemetry, create_traced_httpx_client

from app.database import init_db
from app.routes import agents, missions, tasks

VERSION = "2.0.0"

config = ServiceConfig(service_name="Greenie", port=8080)
registry = ServiceRegistry(service_name="Greenie")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database and register the service on startup."""
    await init_db()
    app.state.http_client = create_traced_httpx_client()
    await registry.register()
    yield
    await registry.deregister()
    await app.state.http_client.aclose()


app = FastAPI(
    title="Greenie",
    description="Evershade agent orchestration and mission control",
    version=VERSION,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Error handlers
register_error_handlers(app)

# Health and metrics endpoints
register_health_routes(app, service_name="Greenie", version=VERSION)

# OpenTelemetry tracing
setup_telemetry(app, service_name="Greenie")

# API routes
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(missions.router, prefix="/api/missions", tags=["missions"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])


@app.get("/api/capabilities")
async def capabilities():
    """Return the list of capabilities and integration status."""
    slinker_url = os.getenv("SLINKER_URL", "")
    trapper_url = os.getenv("TRAPPER_URL", "")
    gobber_url = os.getenv("GOBBER_URL", "")
    shrewd_url = os.getenv("SHREWD_URL", "")

    return {
        "service": "Greenie",
        "version": VERSION,
        "capabilities": [
            "agent_management",
            "mission_planning",
            "task_orchestration",
            "chat_sessions",
            "service_registry",
            "sse_streaming",
            "workflow_engine",
        ],
        "integrations": {
            "opentelemetry": {"enabled": config.telemetry.is_configured},
            "sqlite": {"enabled": True, "path": os.getenv("GREENIE_DB_PATH", "/data/greenie.db")},
            "slinker": {"enabled": bool(slinker_url), "url": slinker_url},
            "trapper": {"enabled": bool(trapper_url), "url": trapper_url},
            "gobber": {"enabled": bool(gobber_url), "url": gobber_url},
            "shrewd": {"enabled": bool(shrewd_url), "url": shrewd_url},
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower(),
    )
