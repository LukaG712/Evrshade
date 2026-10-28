"""Slinker — Task execution with coding agent adapters."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any

from evershade.errors import EvershadeError
from fastapi import APIRouter, HTTPException, Query

from app.adapters import ExecutionRequest
from app.adapters.factory import create_adapter, list_adapters
from app.database import get_db_instance

router = APIRouter(prefix="/api/v1/tasks", tags=["execution"])

# Allowed workspace base directories — execution is restricted to these paths
_ALLOWED_WORKSPACE_BASES = [
    "/tmp/workspace",
    "/workspace",
    "/data/workspace",
    os.getenv("WORKSPACE_BASE", "/tmp/workspace"),
]


def _validate_workspace_path(workspace_path: str) -> str:
    """Validate that workspace path is within allowed directories.

    Args:
        workspace_path: The workspace path to validate.

    Returns:
        The resolved absolute path.

    Raises:
        HTTPException: If the path is not within an allowed directory.
    """
    if not workspace_path:
        return "/tmp/workspace"

    # Resolve to absolute path
    abs_path = os.path.abspath(workspace_path)

    # Check if the path is within an allowed base directory
    for base in _ALLOWED_WORKSPACE_BASES:
        if abs_path.startswith(os.path.abspath(base)):
            return abs_path

    raise HTTPException(
        status_code=400,
        detail=f"Workspace path '{workspace_path}' is not allowed. "
               f"Must be within one of: {_ALLOWED_WORKSPACE_BASES}"
    )


@router.post("", status_code=201)
async def create_task(data: dict[str, Any]):
    """Create and execute a task using a coding agent adapter."""
    task_id = str(uuid.uuid4())
    title = data.get("title", "Untitled task")
    description = data.get("description", "")
    adapter_name = data.get("adapter", "subprocess")
    workspace_path = data.get("workspace_path", "/tmp/workspace")
    files = data.get("files")
    commands = data.get("commands")
    timeout = data.get("timeout", 300)
    permissions = data.get("permissions", {})
    metadata = data.get("metadata", {})

    # Validate workspace path is within allowed directories
    workspace_path = _validate_workspace_path(workspace_path)

    db = await get_db_instance()

    # Create workspace if needed
    workspace_id = None
    if workspace_path:
        workspace_id = str(uuid.uuid4())
        await db.execute(
            """INSERT OR IGNORE INTO workspaces (id, name, path, status, created_at, updated_at)
               VALUES (?, ?, ?, 'active', ?, ?)""",
            (
                workspace_id,
                os.path.basename(workspace_path),
                workspace_path,
                datetime.now(UTC).isoformat(),
                datetime.now(UTC).isoformat(),
            ),
        )

    # Create execution session
    session_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    await db.execute(
        """INSERT INTO execution_sessions (id, task_id, adapter, workspace_id, status,
                                          metadata, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'running', ?, ?, ?)""",
        (
            session_id,
            task_id,
            adapter_name,
            workspace_id,
            json.dumps(metadata),
            now,
            now,
        ),
    )

    # Also create task record for backward compatibility
    await db.execute(
        """INSERT OR IGNORE INTO tasks (id, title, description, status, command,
                                       created_at, updated_at)
           VALUES (?, ?, ?, 'running', ?, ?, ?)""",
        (
            task_id,
            title,
            description,
            description,
            now,
            now,
        ),
    )

    # Build execution request
    request = ExecutionRequest(
        task_id=task_id,
        title=title,
        description=description,
        workspace_path=workspace_path,
        files=files,
        commands=commands,
        timeout=timeout,
        permissions=permissions,
        metadata=metadata,
    )

    # Execute asynchronously
    asyncio.create_task(_execute_task_async(task_id, session_id, adapter_name, request))

    return {
        "id": task_id,
        "title": title,
        "status": "running",
        "adapter": adapter_name,
        "workspace": workspace_path,
        "created_at": now,
    }


async def _execute_task_async(
    task_id: str,
    session_id: str,
    adapter_name: str,
    request: ExecutionRequest,
) -> None:
    """Execute a task asynchronously using the selected adapter."""
    db = await get_db_instance()
    adapter = create_adapter(adapter_name)

    try:
        result = await adapter.execute(request)

        # Update execution session
        now = datetime.now(UTC).isoformat()
        await db.execute(
            """UPDATE execution_sessions SET status = ?, output = ?, error = ?,
               exit_code = ?, duration_ms = ?, completed_at = ?, updated_at = ?
               WHERE id = ?""",
            (
                result.status,
                result.output[:50000],  # Truncate long output
                result.error[:5000] if result.error else None,
                result.exit_code,
                result.duration_ms,
                now,
                now,
                session_id,
            ),
        )

        # Store file changes
        for fc in result.file_changes:
            fc_id = str(uuid.uuid4())
            await db.execute(
                """INSERT INTO file_changes (id, session_id, path, action, diff, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    fc_id,
                    session_id,
                    fc.path,
                    fc.action,
                    fc.diff[:10000] if fc.diff else None,
                    now,
                ),
            )

        # Update task record
        await db.execute(
            """UPDATE tasks SET status = ?, output = ?, error = ?,
               exit_code = ?, completed_at = ?, updated_at = ? WHERE id = ?""",
            (
                result.status,
                result.output[:50000],
                result.error[:5000] if result.error else None,
                result.exit_code,
                now,
                now,
                task_id,
            ),
        )

    except Exception as e:
        now = datetime.now(UTC).isoformat()
        error_msg = str(e)
        await db.execute(
            """UPDATE execution_sessions SET status = 'failed', error = ?,
               completed_at = ?, updated_at = ? WHERE id = ?""",
            (error_msg[:5000], now, now, session_id),
        )
        await db.execute(
            """UPDATE tasks SET status = 'failed', error = ?,
               completed_at = ?, updated_at = ? WHERE id = ?""",
            (error_msg[:5000], now, now, task_id),
        )


@router.get("/{task_id}")
async def get_task(task_id: str):
    """Get task status and results."""
    db = await get_db_instance()

    # Check execution sessions first
    session = await db.fetchone(
        "SELECT * FROM execution_sessions WHERE task_id = ? ORDER BY created_at DESC",
        (task_id,),
    )

    if session:
        session = dict(session)
        session["metadata"] = json.loads(session.get("metadata", "{}"))

        # Get file changes
        changes = await db.fetchall(
            "SELECT * FROM file_changes WHERE session_id = ? ORDER BY created_at",
            (session["id"],),
        )
        session["file_changes"] = [dict(c) for c in changes]

        return session

    # Fallback to tasks table
    task = await db.fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if task:
        return dict(task)

    raise EvershadeError.not_found("Task not found")


@router.get("")
async def list_tasks(
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List tasks."""
    db = await get_db_instance()
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    tasks = await db.fetchall(query, params)
    return [dict(t) for t in tasks]


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    db = await get_db_instance()
    task = await db.fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if not task:
        raise EvershadeError.not_found("Task not found")

    if task["status"] not in ("running", "pending"):
        raise EvershadeError.bad_request(
            f"Cannot cancel task in status: {task['status']}"
        )

    now = datetime.now(UTC).isoformat()
    await db.execute(
        """UPDATE tasks SET status = 'cancelled', completed_at = ?, updated_at = ?
           WHERE id = ?""",
        (now, now, task_id),
    )

    return {"task_id": task_id, "cancelled": True}


@router.get("/adapters")
async def list_available_adapters():
    """List available coding agent adapters."""
    adapters = list_adapters()
    return {"adapters": adapters}


@router.post("/{task_id}/run-tests")
async def run_tests(task_id: str, test_command: str | None = None):
    """Run tests for a task's workspace."""
    db = await get_db_instance()
    session = await db.fetchone(
        "SELECT * FROM execution_sessions WHERE task_id = ? ORDER BY created_at DESC",
        (task_id,),
    )
    if not session:
        raise EvershadeError.not_found("Task not found")

    session = dict(session)
    workspace_path = session.get("workspace_id")
    if not workspace_path:
        raise EvershadeError.bad_request("No workspace associated with this task")

    # Get workspace path
    workspace = await db.fetchone(
        "SELECT path FROM workspaces WHERE id = ?",
        (workspace_path,),
    )
    if not workspace:
        raise EvershadeError.bad_request("Workspace not found")

    adapter = create_adapter(session.get("adapter", "subprocess"))
    result = await adapter.run_tests(
        workspace["path"],
        test_command=test_command,
    )

    return {
        "task_id": task_id,
        "tests": result,
    }


@router.post("/{task_id}/run-lint")
async def run_lint(task_id: str, lint_command: str | None = None):
    """Run linter for a task's workspace."""
    db = await get_db_instance()
    session = await db.fetchone(
        "SELECT * FROM execution_sessions WHERE task_id = ? ORDER BY created_at DESC",
        (task_id,),
    )
    if not session:
        raise EvershadeError.not_found("Task not found")

    session = dict(session)
    workspace_path = session.get("workspace_id")
    if not workspace_path:
        raise EvershadeError.bad_request("No workspace associated with this task")

    workspace = await db.fetchone(
        "SELECT path FROM workspaces WHERE id = ?",
        (workspace_path,),
    )
    if not workspace:
        raise EvershadeError.bad_request("Workspace not found")

    adapter = create_adapter(session.get("adapter", "subprocess"))
    result = await adapter.run_lint(
        workspace["path"],
        lint_command=lint_command,
    )

    return {
        "task_id": task_id,
        "lint": result,
    }


@router.post("/{task_id}/run-build")
async def run_build(task_id: str, build_command: str | None = None):
    """Run build for a task's workspace."""
    db = await get_db_instance()
    session = await db.fetchone(
        "SELECT * FROM execution_sessions WHERE task_id = ? ORDER BY created_at DESC",
        (task_id,),
    )
    if not session:
        raise EvershadeError.not_found("Task not found")

    session = dict(session)
    workspace_path = session.get("workspace_id")
    if not workspace_path:
        raise EvershadeError.bad_request("No workspace associated with this task")

    workspace = await db.fetchone(
        "SELECT path FROM workspaces WHERE id = ?",
        (workspace_path,),
    )
    if not workspace:
        raise EvershadeError.bad_request("Workspace not found")

    adapter = create_adapter(session.get("adapter", "subprocess"))
    result = await adapter.run_build(
        workspace["path"],
        build_command=build_command,
    )

    return {
        "task_id": task_id,
        "build": result,
    }
