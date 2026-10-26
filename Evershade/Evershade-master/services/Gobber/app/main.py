"""Gobber — Main application entry point.

Gobber provides persistent storage, knowledge graph, semantic memory,
webhooks, RBAC, cache, and feature flags for the Evershade ecosystem.
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
from app.routes.storage import router as storage_router
from app.routes.knowledge import router as knowledge_router
from app.routes.memory import router as memory_router

VERSION = "2.0.0"

config = ServiceConfig(service_name="Gobber", port=8085)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()

    # Create traced HTTP client for inter-service calls
    app.state.http_client = create_traced_httpx_client()

    yield

    # Cleanup
    await app.state.http_client.aclose()


app = FastAPI(
    title="Gobber",
    description="Evershade persistent storage, knowledge graph, semantic memory",
    version=VERSION,
    lifespan=lifespan,
)

# Middleware — order matters
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Error handlers
register_error_handlers(app)

# Health and metrics endpoints
register_health_routes(app, service_name="Gobber", version=VERSION)

# OpenTelemetry tracing
setup_telemetry(app, service_name="Gobber")

# Register business routes
app.include_router(storage_router)
app.include_router(knowledge_router)
app.include_router(memory_router)


@app.get("/api/capabilities")
async def capabilities():
    """Return the list of capabilities and integration status."""
    shrewd_url = os.getenv("SHREWD_URL", "")
    vault_path = os.getenv("GOBBER_VAULT_PATH", "")
    return {
        "service": "Gobber",
        "version": VERSION,
        "capabilities": [
            "webhooks", "analytics", "cache", "feature_flags",
            "rbac", "notes", "note_links", "embeddings",
            "semantic_search", "vault_indexing",
            "memory", "memory_context", "memory_relations",
            "knowledge_ingestion", "semantic_memory_search",
        ],
        "integrations": {
            "opentelemetry": {"enabled": config.telemetry.is_configured},
            "shrewd": {
                "enabled": bool(shrewd_url),
                "endpoint": shrewd_url,
            },
            "obsidian_vault": {
                "enabled": bool(vault_path),
                "path": vault_path,
            },
            "memory_system": {
                "enabled": True,
                "features": ["context", "facts", "preferences", "procedures", "observations"],
                "data_separation": ["user", "project", "agent"],
            },
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
