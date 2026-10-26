"""Poltergeist — Main application entry point.

Poltergeist is the notification service for the Evershade platform. It provides:
- Multi-channel notification delivery (Slack, Discord, Email, Telegram)
- Notification templates with Jinja2 rendering
- Async delivery with retry logic
- Delivery history tracking
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
from app.routes import notifications, notification_rules
from app.notifications import NotificationManager

VERSION = "2.0.0"

config_obj = ServiceConfig(service_name="Poltergeist", port=8088)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    await init_db()

    # Create traced HTTP client for inter-service calls
    app.state.http_client = create_traced_httpx_client()

    # Initialize notification manager
    app.state.notification_manager = NotificationManager(db, app.state.http_client)
    await app.state.notification_manager.start_processor()

    yield

    # Stop notification processor
    await app.state.notification_manager.stop_processor()

    # Cleanup
    await app.state.http_client.aclose()


app = FastAPI(
    title="Poltergeist",
    description="Evershade - send notifications through multiple channels with templating and async delivery",
    version=VERSION,
    lifespan=lifespan,
)

# Middleware — order matters
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Error handlers
register_error_handlers(app)

# Health and metrics endpoints
register_health_routes(app, service_name="Poltergeist", version=VERSION)

# OpenTelemetry tracing
setup_telemetry(app, service_name="Poltergeist")

# API routes
app.include_router(notifications.router)
app.include_router(notification_rules.router)


@app.get("/api/capabilities")
async def capabilities():
    """Return the list of capabilities and integration status."""
    return {
        "service": "Poltergeist",
        "version": VERSION,
        "capabilities": [
            "slack",
            "discord",
            "email",
            "telegram",
            "templates",
            "async_delivery",
            "retry_logic",
            "delivery_history",
            "event_driven",
            "user_preferences",
            "notification_rules",
            "delivery_status",
        ],
        "integrations": {
            "opentelemetry": {"enabled": config_obj.telemetry.is_configured},
            "sqlite": {"enabled": True, "path": os.getenv("POLTERGEIST_DB_PATH", "/data/poltergeist.db")},
            "event_driven": {"enabled": True},
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