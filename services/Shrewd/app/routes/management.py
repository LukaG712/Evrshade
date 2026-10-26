"""Shrewd — Provider, model, usage, routing, and privacy routes."""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter

from evershade.errors import EvershadeError

from app.database import db
from app.models import (
    ModelCreate,
    ModelResponse,
    ModelUpdate,
    PrivacyRuleCreate,
    PrivacyRuleResponse,
    ProviderCreate,
    ProviderResponse,
    ProviderUpdate,
    RoutingRuleCreate,
    RoutingRuleResponse,
    UsageRecord,
)

router = APIRouter(prefix="/api", tags=["llm"])


# ─── Providers ────────────────────────────────────────────────────────────────

@router.post("/providers", response_model=ProviderResponse)
async def create_provider(data: ProviderCreate):
    prov_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """INSERT INTO providers (id, name, base_url, api_key, config, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [prov_id, data.name, data.base_url, data.api_key, json.dumps(data.config), now, now],
    )
    return ProviderResponse(
        id=prov_id, name=data.name, base_url=data.base_url,
        enabled=True, created_at=now, updated_at=now,
    )


@router.get("/providers")
async def list_providers():
    rows = await db.fetchall("SELECT * FROM providers ORDER BY name")
    return [
        ProviderResponse(
            id=r["id"], name=r["name"], base_url=r["base_url"],
            enabled=bool(r["enabled"]), created_at=r["created_at"], updated_at=r["updated_at"],
        )
        for r in rows
    ]


@router.get("/providers/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: str):
    row = await db.fetchone("SELECT * FROM providers WHERE id = ?", [provider_id])
    if not row:
        raise EvershadeError.not_found("Provider not found")
    return ProviderResponse(
        id=row["id"], name=row["name"], base_url=row["base_url"],
        enabled=bool(row["enabled"]), created_at=row["created_at"], updated_at=row["updated_at"],
    )


@router.patch("/providers/{provider_id}", response_model=ProviderResponse)
async def update_provider(provider_id: str, data: ProviderUpdate):
    now = datetime.now(timezone.utc).isoformat()
    row = await db.fetchone("SELECT * FROM providers WHERE id = ?", [provider_id])
    if not row:
        raise EvershadeError.not_found("Provider not found")
    updates = ["updated_at = ?"]
    params = [now]
    if data.base_url is not None:
        updates.append("base_url = ?"); params.append(data.base_url)
    if data.api_key is not None:
        updates.append("api_key = ?"); params.append(data.api_key)
    if data.enabled is not None:
        updates.append("enabled = ?"); params.append(1 if data.enabled else 0)
    if data.config is not None:
        updates.append("config = ?"); params.append(json.dumps(data.config))
    params.append(provider_id)
    await db.execute(f"UPDATE providers SET {', '.join(updates)} WHERE id = ?", params)
    updated = await db.fetchone("SELECT * FROM providers WHERE id = ?", [provider_id])
    return ProviderResponse(
        id=updated["id"], name=updated["name"], base_url=updated["base_url"],
        enabled=bool(updated["enabled"]), created_at=updated["created_at"], updated_at=updated["updated_at"],
    )


@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str):
    await db.execute("DELETE FROM providers WHERE id = ?", [provider_id])
    return {"deleted": provider_id}


# ─── Models ───────────────────────────────────────────────────────────────────

@router.post("/models", response_model=ModelResponse)
async def create_model(data: ModelCreate):
    model_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """INSERT INTO models (id, name, provider_id, context_window, max_tokens,
           supports_vision, supports_tools, supports_embeddings,
           input_cost_per_token, output_cost_per_token, config, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [model_id, data.name, data.provider_id, data.context_window, data.max_tokens,
         1 if data.supports_vision else 0, 1 if data.supports_tools else 0,
         1 if data.supports_embeddings else 0,
         data.input_cost_per_token, data.output_cost_per_token,
         json.dumps(data.config), now, now],
    )
    return ModelResponse(
        id=model_id, name=data.name, provider_id=data.provider_id,
        context_window=data.context_window, max_tokens=data.max_tokens,
        supports_vision=data.supports_vision, supports_tools=data.supports_tools,
        supports_embeddings=data.supports_embeddings,
        input_cost_per_token=data.input_cost_per_token,
        output_cost_per_token=data.output_cost_per_token,
        enabled=True, created_at=now, updated_at=now,
    )


@router.get("/models")
async def list_models(provider_id: str = ""):
    if provider_id:
        rows = await db.fetchall(
            "SELECT * FROM models WHERE provider_id = ? ORDER BY name", [provider_id]
        )
    else:
        rows = await db.fetchall("SELECT * FROM models ORDER BY name")
    return [
        ModelResponse(
            id=r["id"], name=r["name"], provider_id=r["provider_id"],
            context_window=r["context_window"], max_tokens=r["max_tokens"],
            supports_vision=bool(r["supports_vision"]), supports_tools=bool(r["supports_tools"]),
            supports_embeddings=bool(r["supports_embeddings"]),
            input_cost_per_token=r["input_cost_per_token"],
            output_cost_per_token=r["output_cost_per_token"],
            enabled=bool(r["enabled"]), created_at=r["created_at"], updated_at=r["updated_at"],
        )
        for r in rows
    ]


@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str):
    row = await db.fetchone("SELECT * FROM models WHERE id = ?", [model_id])
    if not row:
        raise EvershadeError.not_found("Model not found")
    return ModelResponse(
        id=row["id"], name=row["name"], provider_id=row["provider_id"],
        context_window=row["context_window"], max_tokens=row["max_tokens"],
        supports_vision=bool(row["supports_vision"]), supports_tools=bool(row["supports_tools"]),
        supports_embeddings=bool(row["supports_embeddings"]),
        input_cost_per_token=row["input_cost_per_token"],
        output_cost_per_token=row["output_cost_per_token"],
        enabled=bool(row["enabled"]), created_at=row["created_at"], updated_at=row["updated_at"],
    )


@router.patch("/models/{model_id}", response_model=ModelResponse)
async def update_model(model_id: str, data: ModelUpdate):
    now = datetime.now(timezone.utc).isoformat()
    row = await db.fetchone("SELECT * FROM models WHERE id = ?", [model_id])
    if not row:
        raise EvershadeError.not_found("Model not found")
    updates = ["updated_at = ?"]
    params = [now]
    if data.context_window is not None:
        updates.append("context_window = ?"); params.append(data.context_window)
    if data.max_tokens is not None:
        updates.append("max_tokens = ?"); params.append(data.max_tokens)
    if data.supports_vision is not None:
        updates.append("supports_vision = ?"); params.append(1 if data.supports_vision else 0)
    if data.supports_tools is not None:
        updates.append("supports_tools = ?"); params.append(1 if data.supports_tools else 0)
    if data.supports_embeddings is not None:
        updates.append("supports_embeddings = ?"); params.append(1 if data.supports_embeddings else 0)
    if data.input_cost_per_token is not None:
        updates.append("input_cost_per_token = ?"); params.append(data.input_cost_per_token)
    if data.output_cost_per_token is not None:
        updates.append("output_cost_per_token = ?"); params.append(data.output_cost_per_token)
    if data.enabled is not None:
        updates.append("enabled = ?"); params.append(1 if data.enabled else 0)
    if data.config is not None:
        updates.append("config = ?"); params.append(json.dumps(data.config))
    params.append(model_id)
    await db.execute(f"UPDATE models SET {', '.join(updates)} WHERE id = ?", params)
    updated = await db.fetchone("SELECT * FROM models WHERE id = ?", [model_id])
    return ModelResponse(
        id=updated["id"], name=updated["name"], provider_id=updated["provider_id"],
        context_window=updated["context_window"], max_tokens=updated["max_tokens"],
        supports_vision=bool(updated["supports_vision"]), supports_tools=bool(updated["supports_tools"]),
        supports_embeddings=bool(updated["supports_embeddings"]),
        input_cost_per_token=updated["input_cost_per_token"],
        output_cost_per_token=updated["output_cost_per_token"],
        enabled=bool(updated["enabled"]), created_at=updated["created_at"], updated_at=updated["updated_at"],
    )


@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    await db.execute("DELETE FROM models WHERE id = ?", [model_id])
    return {"deleted": model_id}


# ─── Usage ────────────────────────────────────────────────────────────────────

@router.get("/usage")
async def list_usage(model_id: str = "", limit: int = 100):
    if model_id:
        rows = await db.fetchall(
            "SELECT * FROM usage WHERE model_id = ? ORDER BY created_at DESC LIMIT ?",
            [model_id, limit],
        )
    else:
        rows = await db.fetchall(
            "SELECT * FROM usage ORDER BY created_at DESC LIMIT ?", [limit]
        )
    return [
        UsageRecord(
            id=r["id"], model_id=r["model_id"], provider_id=r["provider_id"],
            input_tokens=r["input_tokens"], output_tokens=r["output_tokens"],
            total_tokens=r["total_tokens"], estimated_cost=r["estimated_cost"],
            duration_ms=r["duration_ms"], status=r["status"], created_at=r["created_at"],
        )
        for r in rows
    ]


@router.get("/usage/stats")
async def usage_stats():
    """Return aggregated usage statistics."""
    row = await db.fetchone("""
        SELECT
            COUNT(*) as total_requests,
            SUM(input_tokens) as total_input,
            SUM(output_tokens) as total_output,
            SUM(estimated_cost) as total_cost,
            AVG(duration_ms) as avg_duration
        FROM usage
    """)
    return {
        "total_requests": row["total_requests"] if row else 0,
        "total_input_tokens": row["total_input"] or 0,
        "total_output_tokens": row["total_output"] or 0,
        "total_estimated_cost": row["total_cost"] or 0.0,
        "avg_duration_ms": round(row["avg_duration"] or 0.0, 2),
    }


# ─── Routing Rules ────────────────────────────────────────────────────────────

@router.post("/routing-rules", response_model=RoutingRuleResponse)
async def create_routing_rule(data: RoutingRuleCreate):
    rule_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """INSERT INTO routing_rules (id, name, priority, condition, target_model_id, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [rule_id, data.name, data.priority, json.dumps(data.condition),
         data.target_model_id, now],
    )
    return RoutingRuleResponse(
        id=rule_id, name=data.name, priority=data.priority,
        condition=data.condition, target_model_id=data.target_model_id,
        enabled=True, created_at=now,
    )


@router.get("/routing-rules")
async def list_routing_rules():
    rows = await db.fetchall("SELECT * FROM routing_rules ORDER BY priority DESC")
    return [
        RoutingRuleResponse(
            id=r["id"], name=r["name"], priority=r["priority"],
            condition=json.loads(r["condition"]), target_model_id=r["target_model_id"],
            enabled=bool(r["enabled"]), created_at=r["created_at"],
        )
        for r in rows
    ]


@router.patch("/routing-rules/{rule_id}")
async def update_routing_rule(rule_id: str, enabled: bool | None = None):
    row = await db.fetchone("SELECT * FROM routing_rules WHERE id = ?", [rule_id])
    if not row:
        raise EvershadeError.not_found("Rule not found")
    if enabled is not None:
        await db.execute("UPDATE routing_rules SET enabled = ? WHERE id = ?", [1 if enabled else 0, rule_id])
    return {"id": rule_id, "enabled": enabled}


@router.delete("/routing-rules/{rule_id}")
async def delete_routing_rule(rule_id: str):
    await db.execute("DELETE FROM routing_rules WHERE id = ?", [rule_id])
    return {"deleted": rule_id}


# ─── Privacy Rules ────────────────────────────────────────────────────────────

@router.post("/privacy-rules", response_model=PrivacyRuleResponse)
async def create_privacy_rule(data: PrivacyRuleCreate):
    rule_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """INSERT INTO privacy_rules (id, name, level, allowed_providers, description, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [rule_id, data.name, data.level, json.dumps(data.allowed_providers),
         data.description, now],
    )
    return PrivacyRuleResponse(
        id=rule_id, name=data.name, level=data.level,
        allowed_providers=data.allowed_providers, description=data.description,
        created_at=now,
    )


@router.get("/privacy-rules")
async def list_privacy_rules():
    rows = await db.fetchall("SELECT * FROM privacy_rules ORDER BY level")
    return [
        PrivacyRuleResponse(
            id=r["id"], name=r["name"], level=r["level"],
            allowed_providers=json.loads(r["allowed_providers"]),
            description=r["description"], created_at=r["created_at"],
        )
        for r in rows
    ]


@router.delete("/privacy-rules/{rule_id}")
async def delete_privacy_rule(rule_id: str):
    await db.execute("DELETE FROM privacy_rules WHERE id = ?", [rule_id])
    return {"deleted": rule_id}
