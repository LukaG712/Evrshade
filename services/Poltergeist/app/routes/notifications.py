"""Poltergeist — Notification and template routes.

Send notifications, manage channels and templates, and query delivery history.
"""

from __future__ import annotations

import json
import uuid
import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter

from evershade.errors import EvershadeError

from app.database import db
from app.models import (
    ChannelCreate,
    ChannelResponse,
    ChannelUpdate,
    DeliveryHistoryResponse,
    NotificationCreate,
    NotificationResponse,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)
from app.channels.senders import send_notification

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["notifications"])


# ─── Channels ────────────────────────────────────────────────────────────────

@router.get("/channels", response_model=list[ChannelResponse])
async def list_channels():
    """List all notification channels."""
    rows = await db.fetchall("SELECT * FROM channels ORDER BY name")
    return [ChannelResponse(**{**row, "config": json.loads(row.get("config", "{}")), "enabled": bool(row["enabled"])}) for row in rows]


@router.get("/channels/{channel_id}", response_model=ChannelResponse)
async def get_channel(channel_id: str):
    """Get a single channel."""
    row = await db.fetchone("SELECT * FROM channels WHERE id = ?", (channel_id,))
    if not row:
        raise EvershadeError.not_found(f"Channel {channel_id} not found")
    return ChannelResponse(**{**row, "config": json.loads(row.get("config", "{}")), "enabled": bool(row["enabled"])})


@router.post("/channels", response_model=ChannelResponse, status_code=201)
async def create_channel(channel: ChannelCreate):
    """Create a new notification channel."""
    channel_id = str(uuid.uuid4())
    existing = await db.fetchone("SELECT id FROM channels WHERE name = ?", (channel.name,))
    if existing:
        raise EvershadeError.conflict(f"Channel {channel.name} already exists")
    await db.execute(
        """INSERT INTO channels (id, name, type, config)
           VALUES (?, ?, ?, ?)""",
        (channel_id, channel.name, channel.type, json.dumps(channel.config)),
    )
    row = await db.fetchone("SELECT * FROM channels WHERE id = ?", (channel_id,))
    return ChannelResponse(**{**row, "config": json.loads(row.get("config", "{}")), "enabled": bool(row["enabled"])})


@router.put("/channels/{channel_id}", response_model=ChannelResponse)
async def update_channel(channel_id: str, channel: ChannelUpdate):
    """Update a channel's configuration."""
    updates = channel.model_dump(exclude_none=True)
    if not updates:
        raise EvershadeError.validation_error("No fields to update")

    set_parts = []
    values = []
    for k, v in updates.items():
        if k == "enabled":
            set_parts.append("enabled = ?")
            values.append(1 if v else 0)
        elif k == "config":
            set_parts.append("config = ?")
            values.append(json.dumps(v))
        else:
            set_parts.append(f"{k} = ?")
            values.append(v)
    values.append(channel_id)

    existing = await db.fetchone("SELECT * FROM channels WHERE id = ?", (channel_id,))
    if not existing:
        raise EvershadeError.not_found(f"Channel {channel_id} not found")
    await db.execute(f"UPDATE channels SET {', '.join(set_parts)} WHERE id = ?", values)
    row = await db.fetchone("SELECT * FROM channels WHERE id = ?", (channel_id,))
    return ChannelResponse(**{**row, "config": json.loads(row.get("config", "{}")), "enabled": bool(row["enabled"])})


@router.delete("/channels/{channel_id}", status_code=204)
async def delete_channel(channel_id: str):
    """Delete a channel."""
    existing = await db.fetchone("SELECT * FROM channels WHERE id = ?", (channel_id,))
    if not existing:
        raise EvershadeError.not_found(f"Channel {channel_id} not found")
    await db.execute("DELETE FROM channels WHERE id = ?", (channel_id,))


# ─── Templates ───────────────────────────────────────────────────────────────

@router.get("/templates", response_model=list[TemplateResponse])
async def list_templates():
    """List all notification templates."""
    rows = await db.fetchall("SELECT * FROM templates ORDER BY name")
    return [TemplateResponse(**row) for row in rows]


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """Get a single template."""
    row = await db.fetchone("SELECT * FROM templates WHERE id = ?", (template_id,))
    if not row:
        raise EvershadeError.not_found(f"Template {template_id} not found")
    return TemplateResponse(**row)


@router.post("/templates", response_model=TemplateResponse, status_code=201)
async def create_template(template: TemplateCreate):
    """Create a new notification template."""
    template_id = str(uuid.uuid4())
    existing = await db.fetchone("SELECT id FROM templates WHERE name = ?", (template.name,))
    if existing:
        raise EvershadeError.conflict(f"Template {template.name} already exists")
    await db.execute(
        """INSERT INTO templates (id, name, channel_type, subject, body)
           VALUES (?, ?, ?, ?, ?)""",
        (template_id, template.name, template.channel_type, template.subject, template.body),
    )
    row = await db.fetchone("SELECT * FROM templates WHERE id = ?", (template_id,))
    return TemplateResponse(**row)


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: str, template: TemplateUpdate):
    """Update a template."""
    updates = template.model_dump(exclude_none=True)
    if not updates:
        raise EvershadeError.validation_error("No fields to update")

    set_parts = []
    values = []
    for k, v in updates.items():
        set_parts.append(f"{k} = ?")
        values.append(v)
    values.append(template_id)

    existing = await db.fetchone("SELECT * FROM templates WHERE id = ?", (template_id,))
    if not existing:
        raise EvershadeError.not_found(f"Template {template_id} not found")
    await db.execute(f"UPDATE templates SET {', '.join(set_parts)} WHERE id = ?", values)
    row = await db.fetchone("SELECT * FROM templates WHERE id = ?", (template_id,))
    return TemplateResponse(**row)


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(template_id: str):
    """Delete a template."""
    existing = await db.fetchone("SELECT * FROM templates WHERE id = ?", (template_id,))
    if not existing:
        raise EvershadeError.not_found(f"Template {template_id} not found")
    await db.execute("DELETE FROM templates WHERE id = ?", (template_id,))


# ─── Notifications ───────────────────────────────────────────────────────────

@router.post("/notifications", response_model=NotificationResponse, status_code=201)
async def send_notification_req(notification: NotificationCreate):
    """Queue a notification for delivery."""
    notification_id = str(uuid.uuid4())

    # Resolve channel
    channel = await db.fetchone("SELECT * FROM channels WHERE id = ?", (notification.channel_id,))
    if not channel:
        raise EvershadeError.not_found(f"Channel {notification.channel_id} not found")
    if not channel["enabled"]:
        raise EvershadeError.validation_error(f"Channel {notification.channel_id} is disabled")

    # Resolve template if specified
    body = notification.body
    subject = notification.subject
    if notification.template_name:
        tmpl = await db.fetchone("SELECT * FROM templates WHERE name = ?", (notification.template_name,))
        if tmpl:
            from jinja2 import Template
            try:
                if tmpl["body"]:
                    body = Template(tmpl["body"]).render()
                if tmpl["subject"]:
                    subject = Template(tmpl["subject"]).render()
            except Exception:
                pass  # Use raw body/subject if template fails

    # Queue the notification
    await db.execute(
        """INSERT INTO pending_queue (id, channel_id, channel_type, recipient,
           subject, body, template_name, max_retries, scheduled_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            notification_id,
            notification.channel_id,
            channel["type"],
            notification.recipient,
            subject,
            body,
            notification.template_name,
            notification.max_retries,
            notification.scheduled_at or "",
        ),
    )

    # Record in delivery history
    history_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO delivery_history (id, channel_id, channel_type, recipient,
           subject, body, status)
           VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
        (history_id, notification.channel_id, channel["type"],
         notification.recipient, subject, body),
    )

    # Process immediately in background
    asyncio.create_task(_process_queue())

    return NotificationResponse(
        id=notification_id,
        channel_id=notification.channel_id,
        recipient=notification.recipient,
        subject=subject,
        body=body,
        status="pending",
        created_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


async def _process_queue():
    """Process pending notifications from the queue."""
    # Get pending items
    rows = await db.fetchall(
        """SELECT pq.*, ch.config FROM pending_queue pq
           JOIN channels ch ON pq.channel_id = ch.id
           WHERE pq.scheduled_at = '' OR pq.scheduled_at <= strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
           ORDER BY pq.created_at ASC
           LIMIT 10"""
    )

    for row in rows:
        notification_id = row["id"]
        try:
            config = json.loads(row.get("config", "{}"))
            await send_notification(
                row["channel_type"],
                config,
                row["recipient"],
                row["subject"],
                row["body"],
            )
            # Mark as sent
            await db.execute(
                "UPDATE delivery_history SET status = 'sent', sent_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE id = (SELECT id FROM delivery_history WHERE channel_id = ? AND recipient = ? ORDER BY created_at DESC LIMIT 1)",
                (row["channel_id"], row["recipient"]),
            )
            await db.execute("DELETE FROM pending_queue WHERE id = ?", (notification_id,))
        except Exception as e:
            logger.error(f"Failed to send notification {notification_id}: {e}")
            retry_count = row.get("retry_count", 0)
            max_retries = row.get("max_retries", 3)
            if retry_count < max_retries:
                await db.execute(
                    "UPDATE pending_queue SET retry_count = retry_count + 1 WHERE id = ?",
                    (notification_id,),
                )
                await db.execute(
                    "UPDATE delivery_history SET status = 'retrying', retry_count = retry_count + 1, error_message = ? WHERE id = (SELECT id FROM delivery_history WHERE channel_id = ? AND recipient = ? ORDER BY created_at DESC LIMIT 1)",
                    (str(e), row["channel_id"], row["recipient"]),
                )
            else:
                await db.execute(
                    "UPDATE delivery_history SET status = 'failed', error_message = ? WHERE id = (SELECT id FROM delivery_history WHERE channel_id = ? AND recipient = ? ORDER BY created_at DESC LIMIT 1)",
                    (str(e), row["channel_id"], row["recipient"]),
                )
                await db.execute("DELETE FROM pending_queue WHERE id = ?", (notification_id,))


@router.get("/history", response_model=list[DeliveryHistoryResponse])
async def list_delivery_history(
    channel_id: str | None = None,
    status: str | None = None,
    limit: int = 100,
):
    """List delivery history."""
    conditions = []
    params = []

    if channel_id:
        conditions.append("channel_id = ?")
        params.append(channel_id)
    if status:
        conditions.append("status = ?")
        params.append(status)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    params.append(limit)

    rows = await db.fetchall(
        f"SELECT * FROM delivery_history {where} ORDER BY created_at DESC LIMIT ?",
        params,
    )
    return [DeliveryHistoryResponse(**row) for row in rows]


@router.post("/process-queue", status_code=200)
async def trigger_process_queue():
    """Manually trigger queue processing."""
    await _process_queue()
    return {"status": "processed"}
