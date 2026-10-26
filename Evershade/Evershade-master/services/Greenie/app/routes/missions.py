"""Greenie — Mission control routes.

Manages missions, milestones, features, validation contracts, checkpoints,
approval gates, and mission logs.
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter

from evershade.errors import ErrorCode, EvershadeError

from app.database import get_db_instance
from app.models import (
    ApprovalGateCreate,
    ApprovalGateResponse,
    CheckpointCreate,
    CheckpointResponse,
    FeatureCreate,
    FeatureResponse,
    MilestoneCreate,
    MilestoneResponse,
    MissionCreate,
    MissionResponse,
    MissionUpdate,
    MissionLogCreate,
    MissionLogResponse,
    ValidationContractCreate,
    ValidationContractResponse,
)

router = APIRouter(prefix="/api/missions", tags=["missions"])


# ─── Missions ────────────────────────────────────────────────────────────────

@router.get("", response_model=list[MissionResponse])
async def list_missions(agent_id: str | None = None, status: str | None = None):
    """List missions, optionally filtered by agent or status."""
    db = await get_db_instance()
    conditions = []
    params = []
    if agent_id:
        conditions.append("agent_id = ?")
        params.append(agent_id)
    if status:
        conditions.append("status = ?")
        params.append(status)
    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    rows = await db.fetchall(f"SELECT * FROM missions{where} ORDER BY created_at DESC", params)
    return [MissionResponse(**row) for row in rows]


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(mission_id: str):
    """Get a single mission."""
    db = await get_db_instance()
    row = await db.fetchone("SELECT * FROM missions WHERE id = ?", (mission_id,))
    if not row:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Mission {mission_id} not found")
    return MissionResponse(**row)


@router.post("", response_model=MissionResponse, status_code=201)
async def create_mission(mission: MissionCreate):
    """Create a new mission."""
    mission_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        """INSERT INTO missions (id, name, description, agent_id, autonomy_level)
           VALUES (?, ?, ?, ?, ?)""",
        (mission_id, mission.name, mission.description, mission.agent_id, mission.autonomy_level.value),
    )
    row = await db.fetchone("SELECT * FROM missions WHERE id = ?", (mission_id,))
    return MissionResponse(**row)


@router.patch("/{mission_id}", response_model=MissionResponse)
async def update_mission(mission_id: str, mission: MissionUpdate):
    """Update a mission's status or progress."""
    updates = mission.model_dump(exclude_none=True)
    if not updates:
        raise EvershadeError(ErrorCode.VALIDATION_ERROR, "No fields to update")

    if "status" in updates and hasattr(updates["status"], "value"):
        updates["status"] = updates["status"].value

    # Auto-set timestamps on status change
    if updates.get("status") == "executing" and "started_at" not in updates:
        updates["started_at"] = "strftime('%Y-%m-%dT%H:%M:%SZ', 'now')"
    if updates.get("status") in ("completed", "failed", "cancelled") and "completed_at" not in updates:
        updates["completed_at"] = "strftime('%Y-%m-%dT%H:%M:%SZ', 'now')"

    updates["updated_at"] = "strftime('%Y-%m-%dT%H:%M:%SZ', 'now')"

    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [mission_id]

    db = await get_db_instance()
    row = await db.fetchone("SELECT * FROM missions WHERE id = ?", (mission_id,))
    if not row:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Mission {mission_id} not found")
    await db.execute(f"UPDATE missions SET {set_clause} WHERE id = ?", values)
    row = await db.fetchone("SELECT * FROM missions WHERE id = ?", (mission_id,))
    return MissionResponse(**row)


# ─── Milestones ──────────────────────────────────────────────────────────────

@router.get("/{mission_id}/milestones", response_model=list[MilestoneResponse])
async def list_milestones(mission_id: str):
    """List milestones for a mission."""
    db = await get_db_instance()
    rows = await db.fetchall(
        "SELECT * FROM milestones WHERE mission_id = ? ORDER BY order_index",
        (mission_id,),
    )
    return [MilestoneResponse(**row) for row in rows]


@router.post("/{mission_id}/milestones", response_model=MilestoneResponse, status_code=201)
async def create_milestone(mission_id: str, milestone: MilestoneCreate):
    """Add a milestone to a mission."""
    milestone_id = str(uuid.uuid4())
    db = await get_db_instance()
    mission = await db.fetchone("SELECT id FROM missions WHERE id = ?", (mission_id,))
    if not mission:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Mission {mission_id} not found")
    await db.execute(
        """INSERT INTO milestones (id, mission_id, name, description, order_index)
           VALUES (?, ?, ?, ?, ?)""",
        (milestone_id, mission_id, milestone.name, milestone.description, milestone.order_index),
    )
    row = await db.fetchone("SELECT * FROM milestones WHERE id = ?", (milestone_id,))
    return MilestoneResponse(**row)


# ─── Features ────────────────────────────────────────────────────────────────

@router.get("/milestones/{milestone_id}/features", response_model=list[FeatureResponse])
async def list_features(milestone_id: str):
    """List features for a milestone."""
    db = await get_db_instance()
    rows = await db.fetchall(
        "SELECT * FROM features WHERE milestone_id = ? ORDER BY order_index",
        (milestone_id,),
    )
    return [FeatureResponse(**row) for row in rows]


@router.post("/milestones/{milestone_id}/features", response_model=FeatureResponse, status_code=201)
async def create_feature(milestone_id: str, feature: FeatureCreate):
    """Add a feature to a milestone."""
    feature_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        """INSERT INTO features (id, milestone_id, name, description, order_index)
           VALUES (?, ?, ?, ?, ?)""",
        (feature_id, milestone_id, feature.name, feature.description, feature.order_index),
    )
    row = await db.fetchone("SELECT * FROM features WHERE id = ?", (feature_id,))
    return FeatureResponse(**row)


# ─── Validation Contracts ────────────────────────────────────────────────────

@router.get("/milestones/{milestone_id}/validations", response_model=list[ValidationContractResponse])
async def list_validations(milestone_id: str):
    """List validation contracts for a milestone."""
    db = await get_db_instance()
    rows = await db.fetchall(
        "SELECT * FROM validation_contracts WHERE milestone_id = ?",
        (milestone_id,),
    )
    return [ValidationContractResponse(**row) for row in rows]


@router.post("/milestones/{milestone_id}/validations", response_model=ValidationContractResponse, status_code=201)
async def create_validation(milestone_id: str, vc: ValidationContractCreate):
    """Add a validation contract to a milestone."""
    vc_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        "INSERT INTO validation_contracts (id, milestone_id, criterion) VALUES (?, ?, ?)",
        (vc_id, milestone_id, vc.criterion),
    )
    row = await db.fetchone("SELECT * FROM validation_contracts WHERE id = ?", (vc_id,))
    return ValidationContractResponse(**row)


# ─── Checkpoints ─────────────────────────────────────────────────────────────

@router.get("/{mission_id}/checkpoints", response_model=list[CheckpointResponse])
async def list_checkpoints(mission_id: str):
    """List checkpoints for a mission (for recovery)."""
    db = await get_db_instance()
    rows = await db.fetchall(
        "SELECT * FROM checkpoints WHERE mission_id = ? ORDER BY created_at DESC",
        (mission_id,),
    )
    result = []
    for row in rows:
        row["state"] = json.loads(row["state"]) if row["state"] else {}
        result.append(CheckpointResponse(**row))
    return result


@router.post("/{mission_id}/checkpoints", response_model=CheckpointResponse, status_code=201)
async def create_checkpoint(mission_id: str, cp: CheckpointCreate):
    """Create a checkpoint for mission recovery."""
    cp_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        """INSERT INTO checkpoints (id, mission_id, state, milestone_id)
           VALUES (?, ?, ?, ?)""",
        (cp_id, mission_id, json.dumps(cp.state), cp.milestone_id),
    )
    row = await db.fetchone("SELECT * FROM checkpoints WHERE id = ?", (cp_id,))
    row["state"] = json.loads(row["state"]) if row["state"] else {}
    return CheckpointResponse(**row)


# ─── Approval Gates ──────────────────────────────────────────────────────────

@router.get("/{mission_id}/approvals", response_model=list[ApprovalGateResponse])
async def list_approvals(mission_id: str):
    """List approval gates for a mission."""
    db = await get_db_instance()
    rows = await db.fetchall(
        "SELECT * FROM approval_gates WHERE mission_id = ? ORDER BY created_at DESC",
        (mission_id,),
    )
    return [ApprovalGateResponse(**row) for row in rows]


@router.post("/{mission_id}/approvals", response_model=ApprovalGateResponse, status_code=201)
async def create_approval(mission_id: str, gate: ApprovalGateCreate):
    """Create an approval gate (pauses execution for human review)."""
    gate_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        """INSERT INTO approval_gates (id, mission_id, milestone_id, request)
           VALUES (?, ?, ?, ?)""",
        (gate_id, mission_id, gate.milestone_id, gate.request),
    )
    row = await db.fetchone("SELECT * FROM approval_gates WHERE id = ?", (gate_id,))
    return ApprovalGateResponse(**row)


@router.patch("/{mission_id}/approvals/{gate_id}", response_model=ApprovalGateResponse)
async def resolve_approval(mission_id: str, gate_id: str, approved: bool, response: str = ""):
    """Resolve an approval gate (approve or reject)."""
    db = await get_db_instance()
    row = await db.fetchone("SELECT * FROM approval_gates WHERE id = ? AND mission_id = ?", (gate_id, mission_id))
    if not row:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Approval gate {gate_id} not found")
    status = "approved" if approved else "rejected"
    await db.execute(
        """UPDATE approval_gates SET status = ?, response = ?, resolved_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
           WHERE id = ?""",
        (status, response, gate_id),
    )
    row = await db.fetchone("SELECT * FROM approval_gates WHERE id = ?", (gate_id,))
    return ApprovalGateResponse(**row)


# ─── Mission Logs ────────────────────────────────────────────────────────────

@router.get("/{mission_id}/logs", response_model=list[MissionLogResponse])
async def list_logs(mission_id: str, level: str | None = None, limit: int = 100):
    """List logs for a mission."""
    db = await get_db_instance()
    if level:
        rows = await db.fetchall(
            "SELECT * FROM mission_logs WHERE mission_id = ? AND level = ? ORDER BY created_at DESC LIMIT ?",
            (mission_id, level, limit),
        )
    else:
        rows = await db.fetchall(
            "SELECT * FROM mission_logs WHERE mission_id = ? ORDER BY created_at DESC LIMIT ?",
            (mission_id, limit),
        )
    result = []
    for row in rows:
        row["data"] = json.loads(row["data"]) if row["data"] else {}
        result.append(MissionLogResponse(**row))
    return result


@router.post("/{mission_id}/logs", response_model=MissionLogResponse, status_code=201)
async def add_log(mission_id: str, log: MissionLogCreate):
    """Add a log entry to a mission."""
    log_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        """INSERT INTO mission_logs (id, mission_id, level, message, data)
           VALUES (?, ?, ?, ?, ?)""",
        (log_id, mission_id, log.level.value, log.message, json.dumps(log.data)),
    )
    row = await db.fetchone("SELECT * FROM mission_logs WHERE id = ?", (log_id,))
    row["data"] = json.loads(row["data"]) if row["data"] else {}
    return MissionLogResponse(**row)
