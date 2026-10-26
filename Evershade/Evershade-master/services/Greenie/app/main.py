"""Greenie — Main application entry point.

Greenie is the central hub for the Evershade platform. It provides:
- Agent management (CRUD operations)
- Chat sessions and conversation history
- Mission control (lifecycle, milestones, validation)
- Agent harness (specs, droids, skills, hooks, environments)
- Real-time streaming (SSE and WebSocket)
- API key authentication
- Service registry (central registry host)
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
from evershade.registry import ServiceRegistry, register_service_routes

from app.database import init_db, db
from app.routes import agents, chat, missions, harness, streaming, tasks, workflows
from app.workflow import WorkflowEngine

VERSION = "2.0.0"

config = ServiceConfig(service_name="Greenie", port=8080)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database and register with service registry on startup."""
    await init_db()

    # Set up service registry — Greenie is the central registry host
    app.state.registry = ServiceRegistry()
    register_service_routes(app, app.state.registry)
    app.state.registry.register(
        "Greenie",
        "http://Greenie:8080",
        VERSION,
        capabilities=["agents", "chat", "missions", "registry"],
    )

    # Create traced HTTP client for inter-service calls
    app.state.http_client = create_traced_httpx_client()

    # Initialize workflow engine
    app.state.workflow_engine = WorkflowEngine(db, app.state.http_client)

    yield

    # Cleanup
    await app.state.http_client.aclose()


app = FastAPI(
    title="Greenie",
    description="Evershade central API, orchestration, chat, and dashboard",
    version=VERSION,
    lifespan=lifespan,
)

# Middleware — order matters
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Error handlers
register_error_handlers(app)

# Health and metrics endpoints
register_health_routes(app, service_name="Greenie", version=VERSION)

# OpenTelemetry tracing
setup_telemetry(app, service_name="Greenie")

# API routes
app.include_router(agents.router)
app.include_router(chat.router)
app.include_router(missions.router)
app.include_router(harness.router)
app.include_router(streaming.router)
app.include_router(tasks.router)
app.include_router(workflows.router)


@app.get("/api/capabilities")
async def capabilities():
    """Return the list of capabilities and integration status."""
    return {
        "service": "Greenie",
        "version": VERSION,
        "capabilities": [
            "agents",
            "chat",
            "missions",
            "milestones",
            "features",
            "validation",
            "checkpoints",
            "approvals",
            "specs",
            "droids",
            "skills",
            "hooks",
            "environments",
            "sse",
            "websocket",
            "tasks",
            "task_decomposition",
            "agent_discovery",
            "retry_policies",
            "workflows",
            "workflow_runs",
            "webhooks",
            "workflow_automation",
        ],
        "integrations": {
            "opentelemetry": {"enabled": config.telemetry.is_configured},
            "sqlite": {"enabled": True, "path": os.getenv("GREENIE_DB_PATH", "/data/greenie.db")},
            "registry": {"enabled": True, "host": "Greenie"},
            "task_orchestration": {"enabled": True},
            "slinker_delegation": {"enabled": True},
            "workflow_engine": {"enabled": True},
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
