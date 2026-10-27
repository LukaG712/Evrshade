"""Greenie — Workstation management routes.

Provides CRUD for workstations (isolated execution environments)
with Docker integration for container lifecycle management.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid

from fastapi import APIRouter, HTTPException

from app.database import db

logger = logging.getLogger(__name__)


async def _run_docker(*args: str, timeout: int = 30) -> tuple[int, str, str]:
    """Run a Docker command asynchronously and return (returncode, stdout, stderr)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode or 0, stdout.decode(), stderr.decode()
    except FileNotFoundError:
        return 1, "", "Docker not found"
    except TimeoutError:
        proc.kill()
        await proc.wait()
        return 1, "", "Timeout"


router = APIRouter()


@router.get("/")
async def list_workstations():
    """List all workstations."""
    rows = await db.fetchall("SELECT * FROM workstations ORDER BY created_at DESC")
    workstations = []
    for row in rows:
        d = dict(row)
        d["tags"] = json.loads(d.get("tags", "[]"))
        workstations.append(d)
    return {"workstations": workstations}


@router.get("/stats")
async def get_workstation_stats():
    """Get workstation statistics."""
    total = (await db.fetchone("SELECT COUNT(*) as c FROM workstations"))["c"]
    running = (
        await db.fetchone(
            "SELECT COUNT(*) as c FROM workstations WHERE status = 'running'"
        )
    )["c"]
    stopped = (
        await db.fetchone(
            "SELECT COUNT(*) as c FROM workstations WHERE status = 'stopped'"
        )
    )["c"]
    error = (
        await db.fetchone(
            "SELECT COUNT(*) as c FROM workstations WHERE status = 'error'"
        )
    )["c"]
    # Docker availability is checked at runtime
    docker_available = False
    try:
        rc, _, _ = await _run_docker("docker", "info", timeout=5)
        docker_available = rc == 0
    except Exception:
        pass
    return {
        "total": total,
        "running": running,
        "stopped": stopped,
        "error": error,
        "docker_available": docker_available,
    }


@router.post("/")
async def create_workstation(data: dict):
    """Create a new workstation."""
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Workstation name is required")
    ws_id = str(uuid.uuid4())
    description = data.get("description", "")
    agent_name = data.get("agent_name", "")
    tags = json.dumps(data.get("tags", []))
    await db.execute(
        "INSERT INTO workstations (id, name, description, agent_name, tags) VALUES (?, ?, ?, ?, ?)",
        (ws_id, name, description, agent_name, tags),
    )
    return {"id": ws_id, "name": name, "status": "pending"}


@router.post("/{ws_id}/start")
async def start_workstation(ws_id: str):
    """Start a workstation (create Docker container)."""
    existing = await db.fetchone("SELECT * FROM workstations WHERE id = ?", (ws_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Workstation not found")
    dict(existing)
    # Mark as creating
    await db.execute(
        "UPDATE workstations SET status = 'creating' WHERE id = ?",
        (ws_id,),
    )
    # Attempt to create Docker container
    container_name = f"evershade-ws-{ws_id[:8]}"
    try:
        rc, stdout, stderr = await _run_docker(
            "docker",
            "create",
            "--name",
            container_name,
            "python:3.12-slim",
            "tail",
            "-f",
            "/dev/null",
            timeout=30,
        )
        if rc == 0:
            container_id = stdout.strip()[:12]
            await _run_docker("docker", "start", container_name, timeout=15)
            await db.execute(
                "UPDATE workstations SET status = 'running', container_id = ?, container_name = ?, started_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE id = ?",
                (container_id, container_name, ws_id),
            )
            return {"id": ws_id, "status": "running", "container_id": container_id}
        else:
            raise RuntimeError(stderr)
    except RuntimeError as e:
        logger.error("Failed to start workstation %s: %s", ws_id, e)
        await db.execute(
            "UPDATE workstations SET status = 'error', error = ? WHERE id = ?",
            ("Failed to start container", ws_id),
        )
        raise HTTPException(status_code=500, detail="Failed to start workstation")


@router.post("/{ws_id}/stop")
async def stop_workstation(ws_id: str):
    """Stop a workstation."""
    existing = await db.fetchone("SELECT * FROM workstations WHERE id = ?", (ws_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Workstation not found")
    ws = dict(existing)
    container_name = ws.get("container_name", "")
    if container_name:
        try:
            await _run_docker("docker", "stop", container_name, timeout=30)
        except Exception:
            pass
    await db.execute(
        "UPDATE workstations SET status = 'stopped' WHERE id = ?", (ws_id,)
    )
    return {"id": ws_id, "status": "stopped"}


@router.post("/{ws_id}/destroy")
async def destroy_workstation(ws_id: str):
    """Destroy a workstation and its container."""
    existing = await db.fetchone("SELECT * FROM workstations WHERE id = ?", (ws_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Workstation not found")
    ws = dict(existing)
    container_name = ws.get("container_name", "")
    if container_name:
        try:
            await _run_docker("docker", "rm", "-f", container_name, timeout=30)
        except Exception:
            pass
    await db.execute(
        "UPDATE workstations SET status = 'destroyed' WHERE id = ?", (ws_id,)
    )
    return {"id": ws_id, "status": "destroyed"}


@router.get("/{ws_id}/logs")
async def get_workstation_logs(ws_id: str, tail: int = 100):
    """Get workstation container logs."""
    existing = await db.fetchone("SELECT * FROM workstations WHERE id = ?", (ws_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Workstation not found")
    ws = dict(existing)
    container_name = ws.get("container_name", "")
    if not container_name:
        return {"logs": "No container attached"}
    try:
        _, stdout, stderr = await _run_docker(
            "docker", "logs", "--tail", str(tail), container_name, timeout=10
        )
        return {"logs": stdout + stderr}
    except Exception:
        return {"logs": "Docker not available"}
