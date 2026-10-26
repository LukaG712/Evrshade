"""Gobber — Storage routes: webhooks, analytics, cache, feature flags, RBAC."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx
from fastapi import APIRouter

from evershade.errors import EvershadeError

from app.database import db
from app.models import (
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    CacheSet,
    FeatureFlagCreate,
    FeatureFlagResponse,
    FeatureFlagUpdate,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    UserRoleCreate,
    UserRoleResponse,
    WebhookCreate,
    WebhookResponse,
    WebhookUpdate,
)

router = APIRouter(prefix="/api", tags=["storage"])


# ─── Webhooks ────────────────────────────────────────────────────────────────

@router.post("/webhooks", response_model=WebhookResponse)
async def create_webhook(data: WebhookCreate):
    wh_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO webhooks (id, name, url, method, headers, events, secret)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [wh_id, data.name, data.url, data.method, json.dumps(data.headers),
         json.dumps(data.events), data.secret],
    )
    return WebhookResponse(
        id=wh_id, name=data.name, url=data.url, method=data.method,
        headers=data.headers, events=data.events, enabled=True,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/webhooks")
async def list_webhooks():
    rows = await db.fetchall("SELECT * FROM webhooks ORDER BY created_at DESC")
    result = []
    for r in rows:
        result.append(WebhookResponse(
            id=r["id"], name=r["name"], url=r["url"], method=r["method"],
            headers=json.loads(r["headers"]), events=json.loads(r["events"]),
            enabled=bool(r["enabled"]),
            created_at=r["created_at"], updated_at=r["updated_at"],
        ))
    return result


@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(webhook_id: str):
    row = await db.fetchone("SELECT * FROM webhooks WHERE id = ?", [webhook_id])
    if not row:
        raise EvershadeError.not_found("Webhook not found")
    return WebhookResponse(
        id=row["id"], name=row["name"], url=row["url"], method=row["method"],
        headers=json.loads(row["headers"]), events=json.loads(row["events"]),
        enabled=bool(row["enabled"]),
        created_at=row["created_at"], updated_at=row["updated_at"],
    )


@router.patch("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(webhook_id: str, data: WebhookUpdate):
    row = await db.fetchone("SELECT * FROM webhooks WHERE id = ?", [webhook_id])
    if not row:
        raise EvershadeError.not_found("Webhook not found")
    updates = []
    params = []
    now = datetime.now(timezone.utc).isoformat()
    if data.name is not None:
        updates.append("name = ?"); params.append(data.name)
    if data.url is not None:
        updates.append("url = ?"); params.append(data.url)
    if data.method is not None:
        updates.append("method = ?"); params.append(data.method)
    if data.headers is not None:
        updates.append("headers = ?"); params.append(json.dumps(data.headers))
    if data.events is not None:
        updates.append("events = ?"); params.append(json.dumps(data.events))
    if data.enabled is not None:
        updates.append("enabled = ?"); params.append(1 if data.enabled else 0)
    if data.secret is not None:
        updates.append("secret = ?"); params.append(data.secret)
    if updates:
        updates.append("updated_at = ?"); params.append(now)
        params.append(webhook_id)
        await db.execute(f"UPDATE webhooks SET {', '.join(updates)} WHERE id = ?", params)
    updated = await db.fetchone("SELECT * FROM webhooks WHERE id = ?", [webhook_id])
    return WebhookResponse(
        id=updated["id"], name=updated["name"], url=updated["url"],
        method=updated["method"], headers=json.loads(updated["headers"]),
        events=json.loads(updated["events"]), enabled=bool(updated["enabled"]),
        created_at=updated["created_at"], updated_at=updated["updated_at"],
    )


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str):
    row = await db.fetchone("SELECT * FROM webhooks WHERE id = ?", [webhook_id])
    if not row:
        raise EvershadeError.not_found("Webhook not found")
    await db.execute("DELETE FROM webhooks WHERE id = ?", [webhook_id])
    return {"deleted": webhook_id}


@router.post("/webhooks/{webhook_id}/deliver")
async def deliver_webhook(webhook_id: str, event: str, payload: Optional[dict[str, Any]] = None):
    """Trigger a webhook delivery."""
    row = await db.fetchone("SELECT * FROM webhooks WHERE id = ? AND enabled = 1", [webhook_id])
    if not row:
        raise EvershadeError.not_found("Webhook not found or disabled")
    delivery_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO webhook_deliveries (id, webhook_id, event, payload, status)
           VALUES (?, ?, ?, ?, 'pending')""",
        [delivery_id, webhook_id, event, json.dumps(payload)],
    )
    # Attempt delivery
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.request(
                row["method"], row["url"],
                headers=json.loads(row["headers"]),
                json=payload,
            )
            status = "delivered" if resp.status_code < 400 else "failed"
            await db.execute(
                "UPDATE webhook_deliveries SET status_code = ?, status = ?, response = ?, delivered_at = ?, attempts = 1 WHERE id = ?",
                [resp.status_code, status, resp.text[:1000], datetime.now(timezone.utc).isoformat(), delivery_id],
            )
    except Exception as e:
        await db.execute(
            "UPDATE webhook_deliveries SET status = 'failed', response = ?, attempts = 1 WHERE id = ?",
            [str(e)[:1000], delivery_id],
        )
    return {"delivery_id": delivery_id, "webhook_id": webhook_id}


# ─── Analytics Events ────────────────────────────────────────────────────────

@router.post("/analytics/events", response_model=AnalyticsEventResponse)
async def create_analytics_event(data: AnalyticsEventCreate):
    evt_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO analytics_events (id, event_type, entity_id, entity_type, properties)
           VALUES (?, ?, ?, ?, ?)""",
        [evt_id, data.event_type, data.entity_id, data.entity_type, json.dumps(data.properties)],
    )
    now = datetime.now(timezone.utc).isoformat()
    return AnalyticsEventResponse(
        id=evt_id, event_type=data.event_type, entity_id=data.entity_id,
        entity_type=data.entity_type, properties=data.properties, created_at=now,
    )


@router.get("/analytics/events")
async def list_analytics_events(event_type: str = "", limit: int = 100):
    if event_type:
        rows = await db.fetchall(
            "SELECT * FROM analytics_events WHERE event_type = ? ORDER BY created_at DESC LIMIT ?",
            [event_type, limit],
        )
    else:
        rows = await db.fetchall(
            "SELECT * FROM analytics_events ORDER BY created_at DESC LIMIT ?", [limit]
        )
    return [
        AnalyticsEventResponse(
            id=r["id"], event_type=r["event_type"], entity_id=r["entity_id"],
            entity_type=r["entity_type"], properties=json.loads(r["properties"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


# ─── Cache ────────────────────────────────────────────────────────────────────

@router.post("/cache")
async def set_cache(data: CacheSet):
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=data.ttl_seconds)
    await db.execute(
        """INSERT OR REPLACE INTO cache (key, value, ttl_seconds, created_at, expires_at)
           VALUES (?, ?, ?, ?, ?)""",
        [data.key, data.value, data.ttl_seconds, now.isoformat(), expires.isoformat()],
    )
    return {"key": data.key, "status": "stored"}


@router.get("/cache/{key}")
async def get_cache(key: str):
    now = datetime.now(timezone.utc).isoformat()
    row = await db.fetchone("SELECT * FROM cache WHERE key = ? AND expires_at > ?", [key, now])
    if not row:
        raise EvershadeError.not_found("Cache miss or expired")
    return {"key": key, "value": row["value"]}


@router.delete("/cache/{key}")
async def delete_cache(key: str):
    await db.execute("DELETE FROM cache WHERE key = ?", [key])
    return {"key": key, "status": "deleted"}


@router.delete("/cache")
async def clear_cache():
    """Clear expired cache entries."""
    now = datetime.now(timezone.utc).isoformat()
    await db.execute("DELETE FROM cache WHERE expires_at <= ?", [now])
    return {"status": "cleared"}


# ─── Feature Flags ────────────────────────────────────────────────────────────

@router.post("/flags", response_model=FeatureFlagResponse)
async def create_feature_flag(data: FeatureFlagCreate):
    flag_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """INSERT INTO feature_flags (id, name, description, enabled, config, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [flag_id, data.name, data.description, 1 if data.enabled else 0,
         json.dumps(data.config), now, now],
    )
    return FeatureFlagResponse(
        id=flag_id, name=data.name, description=data.description,
        enabled=data.enabled, config=data.config, created_at=now, updated_at=now,
    )


@router.get("/flags")
async def list_feature_flags():
    rows = await db.fetchall("SELECT * FROM feature_flags ORDER BY name")
    return [
        FeatureFlagResponse(
            id=r["id"], name=r["name"], description=r["description"],
            enabled=bool(r["enabled"]), config=json.loads(r["config"]),
            created_at=r["created_at"], updated_at=r["updated_at"],
        )
        for r in rows
    ]


@router.get("/flags/{flag_name}")
async def get_feature_flag(flag_name: str):
    row = await db.fetchone("SELECT * FROM feature_flags WHERE name = ?", [flag_name])
    if not row:
        raise EvershadeError.not_found("Flag not found")
    return FeatureFlagResponse(
        id=row["id"], name=row["name"], description=row["description"],
        enabled=bool(row["enabled"]), config=json.loads(row["config"]),
        created_at=row["created_at"], updated_at=row["updated_at"],
    )


@router.patch("/flags/{flag_name}", response_model=FeatureFlagResponse)
async def update_feature_flag(flag_name: str, data: FeatureFlagUpdate):
    now = datetime.now(timezone.utc).isoformat()
    row = await db.fetchone("SELECT * FROM feature_flags WHERE name = ?", [flag_name])
    if not row:
        raise EvershadeError.not_found("Flag not found")
    updates = ["updated_at = ?"]
    params = [now]
    if data.enabled is not None:
        updates.append("enabled = ?"); params.append(1 if data.enabled else 0)
    if data.config is not None:
        updates.append("config = ?"); params.append(json.dumps(data.config))
    params.append(flag_name)
    await db.execute(f"UPDATE feature_flags SET {', '.join(updates)} WHERE name = ?", params)
    updated = await db.fetchone("SELECT * FROM feature_flags WHERE name = ?", [flag_name])
    return FeatureFlagResponse(
        id=updated["id"], name=updated["name"], description=updated["description"],
        enabled=bool(updated["enabled"]), config=json.loads(updated["config"]),
        created_at=updated["created_at"], updated_at=updated["updated_at"],
    )


@router.delete("/flags/{flag_name}")
async def delete_feature_flag(flag_name: str):
    await db.execute("DELETE FROM feature_flags WHERE name = ?", [flag_name])
    return {"deleted": flag_name}


# ─── RBAC Roles ───────────────────────────────────────────────────────────────

@router.post("/roles", response_model=RoleResponse)
async def create_role(data: RoleCreate):
    role_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "INSERT INTO roles (id, name, description, permissions, created_at) VALUES (?, ?, ?, ?, ?)",
        [role_id, data.name, data.description, json.dumps(data.permissions), now],
    )
    return RoleResponse(id=role_id, name=data.name, description=data.description,
                        permissions=data.permissions, created_at=now)


@router.get("/roles")
async def list_roles():
    rows = await db.fetchall("SELECT * FROM roles ORDER BY name")
    return [
        RoleResponse(id=r["id"], name=r["name"], description=r["description"],
                     permissions=json.loads(r["permissions"]), created_at=r["created_at"])
        for r in rows
    ]


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: str):
    row = await db.fetchone("SELECT * FROM roles WHERE id = ?", [role_id])
    if not row:
        raise EvershadeError.not_found("Role not found")
    return RoleResponse(id=row["id"], name=row["name"], description=row["description"],
                        permissions=json.loads(row["permissions"]), created_at=row["created_at"])


@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: str, data: RoleUpdate):
    row = await db.fetchone("SELECT * FROM roles WHERE id = ?", [role_id])
    if not row:
        raise EvershadeError.not_found("Role not found")
    updates = []
    params = []
    if data.name is not None:
        updates.append("name = ?"); params.append(data.name)
    if data.description is not None:
        updates.append("description = ?"); params.append(data.description)
    if data.permissions is not None:
        updates.append("permissions = ?"); params.append(json.dumps(data.permissions))
    if updates:
        params.append(role_id)
        await db.execute(f"UPDATE roles SET {', '.join(updates)} WHERE id = ?", params)
    updated = await db.fetchone("SELECT * FROM roles WHERE id = ?", [role_id])
    return RoleResponse(id=updated["id"], name=updated["name"], description=updated["description"],
                        permissions=json.loads(updated["permissions"]), created_at=updated["created_at"])


@router.delete("/roles/{role_id}")
async def delete_role(role_id: str):
    await db.execute("DELETE FROM roles WHERE id = ?", [role_id])
    return {"deleted": role_id}


# ─── User Roles ───────────────────────────────────────────────────────────────

@router.post("/user-roles", response_model=UserRoleResponse)
async def assign_user_role(data: UserRoleCreate):
    ur_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "INSERT INTO user_roles (id, user_id, role_id, created_at) VALUES (?, ?, ?, ?)",
        [ur_id, data.user_id, data.role_id, now],
    )
    return UserRoleResponse(id=ur_id, user_id=data.user_id, role_id=data.role_id, created_at=now)


@router.get("/user-roles/{user_id}")
async def list_user_roles(user_id: str):
    rows = await db.fetchall(
        "SELECT ur.*, r.name as role_name FROM user_roles ur JOIN roles r ON ur.role_id = r.id WHERE ur.user_id = ?",
        [user_id],
    )
    return [
        {"id": r["id"], "user_id": r["user_id"], "role_id": r["role_id"],
         "role_name": r["role_name"], "created_at": r["created_at"]}
        for r in rows
    ]


@router.delete("/user-roles/{user_id}/{role_id}")
async def remove_user_role(user_id: str, role_id: str):
    await db.execute("DELETE FROM user_roles WHERE user_id = ? AND role_id = ?", [user_id, role_id])
    return {"user_id": user_id, "role_id": role_id, "status": "removed"}
