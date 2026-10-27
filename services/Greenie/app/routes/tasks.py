"""Greenie — Task management routes."""

from __future__ import annotations

import json
from fastapi import APIRouter, HTTPException

from app.database import db
from app.models import TaskCreate, TaskResponse, gen_id

router = APIRouter()


@router.post("/", status_code=201)
async def create_task(task: TaskCreate) -> TaskResponse:
    """Create a new task."""
    tid = gen_id()
    await db.execute(
        "INSERT INTO tasks (id, mission_id, name, description, type, payload) VALUES (?, ?, ?, ?, ?, ?)",
        (tid, task.mission_id, task.name, task.description, task.task_type, json.dumps(task.payload)),
    )
    row = await db.fetchone("SELECT * FROM tasks WHERE id = ?", (tid,))
    return TaskResponse(**row)


@router.get("/")
async def list_tasks() -> list[TaskResponse]:
    """List all tasks."""
    rows = await db.fetchall("SELECT * FROM tasks ORDER BY created_at DESC")
    return [TaskResponse(**r) for r in rows]


@router.get("/{task_id}")
async def get_task(task_id: str) -> TaskResponse:
    """Get a task by ID."""
    row = await db.fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**row)


@router.post("/{task_id}/start")
async def start_task(task_id: str) -> TaskResponse:
    """Start a task."""
    await db.execute(
        "UPDATE tasks SET status = 'running', started_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE id = ?",
        (task_id,),
    )
    row = await db.fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**row)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str) -> None:
    """Delete a task."""
    cursor = await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
