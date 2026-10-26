"""Sneaker — Main application entry point.

Sneaker is the observability service for the Evershade platform. It provides:
- OTLP ingest endpoints for traces, logs, and metrics
- Query endpoints for searching stored telemetry data
- Alert rules management and evaluation
- Prometheus-compatible /metrics export
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
from app.routes import otlp, query, alerts, correlation
from app.correlation import ObservabilityCorrelator

VERSION = "2.0.0"

config = ServiceConfig(service_name="Sneaker", port=8086)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    await init_db()

    # Create traced HTTP client for inter-service calls
    app.state.http_client = create_traced_httpx_client()

    # Initialize observability correlator
    app.state.correlator = ObservabilityCorrelator(db, app.state.http_client)

    yield

    # Cleanup
    await app.state.http_client.aclose()


app = FastAPI(
    title="Sneaker",
    description="Evershade - collect and query metrics, distributed traces, and structured logs",
    version=VERSION,
    lifespan=lifespan,
)

# Middleware — order matters
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Error handlers
register_error_handlers(app)

# Health and metrics endpoints
register_health_routes(app, service_name="Sneaker", version=VERSION)

# OpenTelemetry tracing
setup_telemetry(app, service_name="Sneaker")

# OTLP ingest routes
app.include_router(otlp.router)

# Query routes
app.include_router(query.router)

# Alert routes
app.include_router(alerts.router)
app.include_router(correlation.router)


@app.get("/api/capabilities")
async def capabilities():
    """Return the list of capabilities and integration status."""
    return {
        "service": "Sneaker",
        "version": VERSION,
        "capabilities": [
            "otlp_traces",
            "otlp_logs",
            "otlp_metrics",
            "trace_query",
            "log_query",
            "metric_query",
            "alert_rules",
            "alert_evaluation",
            "trace_correlation",
            "service_health",
            "ai_observability",
            "loki_integration",
            "tempo_integration",
            "dashboard_data",
        ],
        "integrations": {
            "opentelemetry": {"enabled": config.telemetry.is_configured},
            "sqlite": {"enabled": True, "path": os.getenv("SNEAKER_DB_PATH", "/data/sneaker.db")},
            "loki": {"enabled": True, "url": "http://loki:3100"},
            "tempo": {"enabled": True, "url": "http://tempo:3200"},
            "langfuse": {"enabled": True, "url": "http://langfuse:3000"},
            "opik": {"enabled": True, "url": "http://opik:8080"},
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