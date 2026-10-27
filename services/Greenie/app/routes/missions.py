"""Greenie — Mission management routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.database import db
from app.models import MissionCreate, MissionResponse, gen_id

router = APIRouter()


@router.post("/", status_code=201)
async def create_mission(mission: MissionCreate) -> MissionResponse:
    """Create a new mission."""
    mid = gen_id()
    await db.execute(
        "INSERT INTO missions (id, name, description, agent_id) VALUES (?, ?, ?, ?)",
        (mid, mission.name, mission.description, mission.agent_id),
    )
    row = await db.fetchone("SELECT * FROM missions WHERE id = ?", (mid,))
    return MissionResponse(**row)


@router.get("/")
async def list_missions() -> list[MissionResponse]:
    """List all missions."""
    rows = await db.fetchall("SELECT * FROM missions ORDER BY created_at DESC")
    return [MissionResponse(**r) for r in rows]


@router.get("/{mission_id}")
async def get_mission(mission_id: str) -> MissionResponse:
    """Get a mission by ID."""
    row = await db.fetchone("SELECT * FROM missions WHERE id = ?", (mission_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Mission not found")
    return MissionResponse(**row)


@router.post("/{mission_id}/start")
async def start_mission(mission_id: str) -> MissionResponse:
    """Start a mission."""
    await db.execute(
        "UPDATE missions SET status = 'running', started_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE id = ?",
        (mission_id,),
    )
    row = await db.fetchone("SELECT * FROM missions WHERE id = ?", (mission_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Mission not found")
    return MissionResponse(**row)


@router.delete("/{mission_id}", status_code=204)
async def delete_mission(mission_id: str) -> None:
    """Delete a mission."""
    cursor = await db.execute("DELETE FROM missions WHERE id = ?", (mission_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Mission not found")
