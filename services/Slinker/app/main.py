"""Slinker — Main application entry point.

Slinker is the code execution engine for the Evershade platform. It provides:
- Task execution in isolated Git worktrees
- Worker registry with semaphore-based concurrency
- Project registration and Git worktree management
- Session logging and tracking
- OpenAI-compatible endpoints (/v1/chat/completions, /v1/models)
- Junie CLI integration (optional)
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
from app.routes import execution, openai

VERSION = "2.0.0"

config = ServiceConfig(service_name="Slinker", port=8000)

# API key authentication
API_KEY = os.getenv("API_KEY", "")

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
    if request.url.path in PUBLIC_PATHS or not API_KEY:
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
    title="Slinker",
    description="Evershade code execution engine, Junie CLI runner",
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
register_health_routes(app, service_name="Slinker", version=VERSION)

# OpenTelemetry tracing
setup_telemetry(app, service_name="Slinker")

# API routes
app.include_router(execution.router)
app.include_router(openai.router)


@app.get("/api/capabilities")
async def capabilities():
    """Return the list of capabilities and integration status."""
    shrewd_url = os.getenv("SHREWD_URL", "")
    ollama_url = os.getenv("OLLAMA_URL", "")

    return {
        "service": "Slinker",
        "version": VERSION,
        "capabilities": [
            "task_execution",
            "worker_registry",
            "project_management",
            "session_logging",
            "openai_compatible",
            "git_worktrees",
        ],
        "integrations": {
            "opentelemetry": {"enabled": config.telemetry.is_configured},
            "sqlite": {
                "enabled": True,
                "path": os.getenv("SLINKER_DB_PATH", "/data/slinker.db"),
            },
            "shrewd": {"enabled": bool(shrewd_url), "url": shrewd_url},
            "ollama": {"enabled": bool(ollama_url), "url": ollama_url},
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
