"""FastAPI application for Poltergeist notification service.

Delivers real notifications via Slack, Discord, Email, Telegram, and webhooks.
Persists notifications and templates in SQLite.
"""

import asyncio
import hmac
import logging
import os
import time
from datetime import UTC, datetime
from typing import Any

from collections import defaultdict
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Histogram,
        generate_latest,
    )

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

from poltergeist.delivery import get_delivery
from poltergeist.models import Channel, Notification, NotificationStatus, Template
from poltergeist.storage import Storage

logger = logging.getLogger("poltergeist")

app = FastAPI(
    title="Poltergeist",
    description="Notification and messaging hub for the Evershade ecosystem",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

_api_key_raw = os.getenv("API_KEY")
if not _api_key_raw:
    raise RuntimeError(
        "API_KEY environment variable is not set. Refusing to start Poltergeist without a configured API key."
    )
API_KEY = _api_key_raw
storage = Storage(db_path=os.getenv("DB_PATH", "/app/data/poltergeist.db"))

# Max retry attempts for failed deliveries
MAX_RETRIES = int(os.getenv("POLTERGEIST_MAX_RETRIES", "3"))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware for Poltergeist."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._window = 60

    def _get_client_ip(self, request: Request) -> str:
        if request.client:
            return request.client.host
        return "unknown"

    def _is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - self._window
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if ts > window_start
        ]
        return len(self._requests[client_ip]) >= self.requests_per_minute

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/metrics"):
            return await call_next(request)
        client_ip = self._get_client_ip(request)
        if self._is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
                headers={"Retry-After": "60"},
            )
        self._requests[client_ip].append(time.time())
        return await call_next(request)


def verify_bearer(authorization: str | None = Header(None)) -> None:
    """Verify Bearer token in Authorization header."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header. Use: Authorization: Bearer <key>",
        )
    if not hmac.compare_digest(token, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


async def _deliver(notification: Notification) -> None:
    """Deliver a notification with retry logic."""
    channel_str = notification.channel.value
    delivery = get_delivery(channel_str)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            await delivery.send(notification)
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(UTC)
            storage.update_notification_status(
                str(notification.id),
                NotificationStatus.SENT,
                sent_at=notification.sent_at,
            )
            logger.info(f"Notification {notification.id} delivered via {channel_str}")
            return
        except Exception as e:
            logger.warning(
                f"Delivery attempt {attempt} failed for {notification.id}: {e}"
            )
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2**attempt)  # Exponential backoff
            notification.error = str(e)

    # All retries exhausted
    notification.status = NotificationStatus.FAILED
    storage.update_notification_status(
        str(notification.id),
        NotificationStatus.FAILED,
        error=notification.error,
    )
    logger.error(
        f"Notification {notification.id} failed after {MAX_RETRIES} attempts: {notification.error}"
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "Poltergeist"}


# ─── Prometheus Metrics ─────────────────────────────────────────

if HAS_PROMETHEUS:
    poltergeist_http_requests_total = Counter(
        "poltergeist_http_requests_total",
        "Total HTTP requests to Poltergeist",
        ["method", "endpoint", "status"],
    )
    poltergeist_http_request_duration = Histogram(
        "poltergeist_http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "endpoint"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    )

    @app.middleware("http")
    async def prometheus_middleware(request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        method = request.method
        endpoint = request.url.path
        start = time.time()
        status = "200"
        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception:
            status = "500"
        finally:
            duration = time.time() - start
            poltergeist_http_requests_total.labels(
                method=method, endpoint=endpoint, status=status
            ).inc()
            poltergeist_http_request_duration.labels(
                method=method, endpoint=endpoint
            ).observe(duration)
        return response

    @app.get("/metrics")
    async def prometheus_metrics(authorization: str | None = Header(None)):
        """Prometheus metrics endpoint for Grafana scraping."""
        verify_bearer(authorization)
        return Response(
            content=generate_latest().decode("utf-8"),
            media_type=CONTENT_TYPE_LATEST,
        )


@app.get("/api/capabilities")
async def capabilities(authorization: str | None = Header(None)) -> dict:
    """Return service identification, version, and features."""
    verify_bearer(authorization)
    return {
        "service": "Poltergeist",
        "version": "1.1.0",
        "features": [
            "slack",
            "discord",
            "email",
            "telegram",
            "async_delivery",
            "retries",
            "prometheus_metrics",
            "opentelemetry",
        ],
    }


# ─── Notifications ──────────────────────────────────────────────


@app.post("/api/notifications")
async def send_notification(
    data: dict[str, Any], authorization: str | None = Header(None)
) -> dict[str, Any]:
    """Send a notification via the specified channel.

    Supports real delivery to Slack, Discord, Email, Telegram, and webhooks.
    Falls back to simulated delivery if the channel is not configured.
    """
    verify_bearer(authorization)
    notification = Notification(
        channel=Channel(data["channel"]),
        recipient=data["recipient"],
        title=data.get("title", ""),
        message=data["message"],
        metadata=data.get("metadata"),
    )
    # Persist as pending
    storage.create_notification(notification)

    # Attempt real delivery
    try:
        await _deliver(notification)
    except Exception as e:
        logger.error(f"Delivery failed: {e}")
        notification.status = NotificationStatus.FAILED
        notification.error = str(e)
        storage.update_notification_status(
            str(notification.id),
            NotificationStatus.FAILED,
            error=str(e),
        )

    return notification.to_dict()


@app.get("/api/notifications")
async def list_notifications(
    channel: str | None = None,
    status: str | None = None,
    limit: int = 50,
    authorization: str | None = Header(None),
) -> list[dict[str, Any]]:
    """List notifications with optional filtering."""
    verify_bearer(authorization)
    rows = storage.list_notifications(channel=channel, status=status, limit=limit)
    return [
        {
            "id": r["id"],
            "channel": r["channel"],
            "recipient": r["recipient"],
            "title": r["title"],
            "message": r["message"],
            "status": r["status"],
            "created_at": r["created_at"],
            "sent_at": r["sent_at"],
            "error": r["error"],
        }
        for r in rows
    ]


@app.get("/api/notifications/{notification_id}")
async def get_notification(
    notification_id: str,
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    """Get a notification by ID."""
    verify_bearer(authorization)
    row = storage.get_notification(notification_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {
        "id": row["id"],
        "channel": row["channel"],
        "recipient": row["recipient"],
        "title": row["title"],
        "message": row["message"],
        "status": row["status"],
        "created_at": row["created_at"],
        "sent_at": row["sent_at"],
        "error": row["error"],
    }


# ─── Templates ──────────────────────────────────────────────────


@app.post("/api/templates")
async def create_template(
    data: dict[str, Any], authorization: str | None = Header(None)
) -> dict[str, Any]:
    """Create a notification template."""
    verify_bearer(authorization)
    template = Template(
        name=data["name"],
        channel=Channel(data["channel"]),
        subject=data.get("subject", ""),
        body=data["body"],
        variables=data.get("variables"),
    )
    storage.create_template(template)
    return template.to_dict()


@app.get("/api/templates")
async def list_templates(
    authorization: str | None = Header(None),
) -> list[dict[str, Any]]:
    """List all notification templates."""
    verify_bearer(authorization)
    rows = storage.list_templates()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "channel": r["channel"],
            "subject": r["subject"],
            "body": r["body"],
            "variables": r["variables"],
        }
        for r in rows
    ]


@app.get("/api/templates/{name}")
async def get_template(
    name: str, authorization: str | None = Header(None)
) -> dict[str, Any]:
    """Get a template by name."""
    verify_bearer(authorization)
    row = storage.get_template(name)
    if row is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "id": row["id"],
        "name": row["name"],
        "channel": row["channel"],
        "subject": row["subject"],
        "body": row["body"],
        "variables": row["variables"],
    }


@app.post("/api/templates/{name}/send")
async def send_from_template(
    name: str,
    data: dict[str, Any],
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    """Send a notification using a template."""
    verify_bearer(authorization)
    row = storage.get_template(name)
    if row is None:
        raise HTTPException(status_code=404, detail="Template not found")

    # Reconstruct template for rendering
    template = Template(
        name=row["name"],
        channel=Channel(row["channel"]),
        subject=row["subject"],
        body=row["body"],
        variables=[],
    )
    rendered = template.render(**data.get("variables", {}))
    notification = Notification(
        channel=template.channel,
        recipient=data["recipient"],
        title=rendered["subject"],
        message=rendered["body"],
    )
    storage.create_notification(notification)

    try:
        await _deliver(notification)
    except Exception as e:
        notification.status = NotificationStatus.FAILED
        notification.error = str(e)
        storage.update_notification_status(
            str(notification.id),
            NotificationStatus.FAILED,
            error=str(e),
        )

    return notification.to_dict()


@app.delete("/api/templates/{name}")
async def delete_template(
    name: str, authorization: str | None = Header(None)
) -> dict[str, bool]:
    """Delete a template by name."""
    verify_bearer(authorization)
    deleted = storage.delete_template(name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"deleted": True}
