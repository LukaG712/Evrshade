"""Greenie — Agent Harness routes.

Manages specs, droids, skills, hooks, and environments.
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter

from evershade.errors import ErrorCode, EvershadeError

from app.database import get_db_instance
from app.models import (
    DroidCreate,
    DroidResponse,
    EnvironmentCreate,
    EnvironmentResponse,
    HookCreate,
    HookResponse,
    SkillCreate,
    SkillResponse,
    SpecCreate,
    SpecResponse,
    SpecUpdate,
)

router = APIRouter(prefix="/api/harness", tags=["harness"])


# ─── Specs ───────────────────────────────────────────────────────────────────

@router.get("/specs", response_model=list[SpecResponse])
async def list_specs():
    """List all specs."""
    db = await get_db_instance()
    rows = await db.fetchall("SELECT * FROM specs ORDER BY created_at DESC")
    return [SpecResponse(**row) for row in rows]


@router.post("/specs", response_model=SpecResponse, status_code=201)
async def create_spec(spec: SpecCreate):
    """Create a new spec (read-only research before implementation)."""
    spec_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        "INSERT INTO specs (id, title, description) VALUES (?, ?, ?)",
        (spec_id, spec.title, spec.description),
    )
    row = await db.fetchone("SELECT * FROM specs WHERE id = ?", (spec_id,))
    return SpecResponse(**row)


@router.patch("/specs/{spec_id}", response_model=SpecResponse)
async def update_spec(spec_id: str, spec: SpecUpdate):
    """Update a spec's status or research notes."""
    updates = spec.model_dump(exclude_none=True)
    if not updates:
        raise EvershadeError(ErrorCode.VALIDATION_ERROR, "No fields to update")
    if "status" in updates and hasattr(updates["status"], "value"):
        updates["status"] = updates["status"].value
    updates["updated_at"] = "strftime('%Y-%m-%dT%H:%M:%SZ', 'now')"

    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [spec_id]

    db = await get_db_instance()
    row = await db.fetchone("SELECT * FROM specs WHERE id = ?", (spec_id,))
    if not row:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Spec {spec_id} not found")
    await db.execute(f"UPDATE specs SET {set_clause} WHERE id = ?", values)
    row = await db.fetchone("SELECT * FROM specs WHERE id = ?", (spec_id,))
    return SpecResponse(**row)


# ─── Droids ──────────────────────────────────────────────────────────────────

@router.get("/droids", response_model=list[DroidResponse])
async def list_droids():
    """List all custom droids (specialized subagents)."""
    db = await get_db_instance()
    rows = await db.fetchall("SELECT * FROM droids WHERE enabled = 1 ORDER BY name")
    result = []
    for row in rows:
        row["trigger_phrases"] = json.loads(row["trigger_phrases"]) if row["trigger_phrases"] else []
        row["config"] = json.loads(row["config"]) if row["config"] else {}
        row["enabled"] = bool(row["enabled"])
        result.append(DroidResponse(**row))
    return result


@router.post("/droids", response_model=DroidResponse, status_code=201)
async def create_droid(droid: DroidCreate):
    """Register a new custom droid."""
    droid_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        """INSERT INTO droids (id, name, description, trigger_phrases, config, source)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (droid_id, droid.name, droid.description, json.dumps(droid.trigger_phrases),
         json.dumps(droid.config), droid.source),
    )
    row = await db.fetchone("SELECT * FROM droids WHERE id = ?", (droid_id,))
    row["trigger_phrases"] = json.loads(row["trigger_phrases"]) if row["trigger_phrases"] else []
    row["config"] = json.loads(row["config"]) if row["config"] else {}
    row["enabled"] = bool(row["enabled"])
    return DroidResponse(**row)


# ─── Skills ──────────────────────────────────────────────────────────────────

@router.get("/skills", response_model=list[SkillResponse])
async def list_skills():
    """List all available skills (reusable workflows)."""
    db = await get_db_instance()
    rows = await db.fetchall("SELECT * FROM skills WHERE enabled = 1 ORDER BY name")
    result = []
    for row in rows:
        row["trigger_phrases"] = json.loads(row["trigger_phrases"]) if row["trigger_phrases"] else []
        row["steps"] = json.loads(row["steps"]) if row["steps"] else []
        row["enabled"] = bool(row["enabled"])
        result.append(SkillResponse(**row))
    return result


@router.post("/skills", response_model=SkillResponse, status_code=201)
async def create_skill(skill: SkillCreate):
    """Register a new skill."""
    skill_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        """INSERT INTO skills (id, name, description, trigger_phrases, steps)
           VALUES (?, ?, ?, ?, ?)""",
        (skill_id, skill.name, skill.description, json.dumps(skill.trigger_phrases),
         json.dumps(skill.steps)),
    )
    row = await db.fetchone("SELECT * FROM skills WHERE id = ?", (skill_id,))
    row["trigger_phrases"] = json.loads(row["trigger_phrases"]) if row["trigger_phrases"] else []
    row["steps"] = json.loads(row["steps"]) if row["steps"] else []
    row["enabled"] = bool(row["enabled"])
    return SkillResponse(**row)


# ─── Hooks ───────────────────────────────────────────────────────────────────

@router.get("/hooks", response_model=list[HookResponse])
async def list_hooks():
    """List all lifecycle hooks."""
    db = await get_db_instance()
    rows = await db.fetchall("SELECT * FROM hooks WHERE enabled = 1 ORDER BY event, name")
    result = []
    for row in rows:
        row["config"] = json.loads(row["config"]) if row["config"] else {}
        row["enabled"] = bool(row["enabled"])
        result.append(HookResponse(**row))
    return result


@router.post("/hooks", response_model=HookResponse, status_code=201)
async def create_hook(hook: HookCreate):
    """Register a new lifecycle hook."""
    hook_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        """INSERT INTO hooks (id, name, event, action, config)
           VALUES (?, ?, ?, ?, ?)""",
        (hook_id, hook.name, hook.event, hook.action, json.dumps(hook.config)),
    )
    row = await db.fetchone("SELECT * FROM hooks WHERE id = ?", (hook_id,))
    row["config"] = json.loads(row["config"]) if row["config"] else {}
    row["enabled"] = bool(row["enabled"])
    return HookResponse(**row)


# ─── Environments ────────────────────────────────────────────────────────────

@router.get("/environments", response_model=list[EnvironmentResponse])
async def list_environments():
    """List all sandbox environments."""
    db = await get_db_instance()
    rows = await db.fetchall("SELECT * FROM environments ORDER BY name")
    result = []
    for row in rows:
        row["config"] = json.loads(row["config"]) if row["config"] else {}
        row["validated"] = bool(row["validated"])
        result.append(EnvironmentResponse(**row))
    return result


@router.post("/environments", response_model=EnvironmentResponse, status_code=201)
async def create_environment(env: EnvironmentCreate):
    """Create a new sandbox environment definition."""
    env_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        """INSERT INTO environments (id, name, description, config)
           VALUES (?, ?, ?, ?)""",
        (env_id, env.name, env.description, json.dumps(env.config)),
    )
    row = await db.fetchone("SELECT * FROM environments WHERE id = ?", (env_id,))
    row["config"] = json.loads(row["config"]) if row["config"] else {}
    row["validated"] = bool(row["validated"])
    return EnvironmentResponse(**row)
