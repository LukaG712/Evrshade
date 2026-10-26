"""Greenie — Workflow and webhook API routes.

Endpoints for workflow definitions, execution, run tracking, and webhook handling.
"""

from __future__ import annotations

import json
import uuid
import hmac
import hashlib
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request

from evershade.errors import EvershadeError

from app.database import db

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


# ─── Workflow Definitions ────────────────────────────────────────────────────

@router.get("", response_model=list[Dict[str, Any]])
async def list_workflows():
    """List all workflow definitions."""
    rows = await db.fetchall("SELECT * FROM workflows ORDER BY created_at DESC")
    return [
        {
            **row,
            "steps": json.loads(row.get("steps", "[]")),
            "triggers": json.loads(row.get("triggers", "[]")),
            "metadata": json.loads(row.get("metadata", "{}")),
        }
        for row in rows
    ]


@router.post("", status_code=201)
async def create_workflow(request: Request) -> Dict[str, Any]:
    """Create a new workflow definition."""
    body = await request.json()

    workflow_id = str(uuid.uuid4())
    name = body.get("name", "")
    if not name:
        raise EvershadeError.validation_error("name is required")

    description = body.get("description", "")
    steps = body.get("steps", [])
    triggers = body.get("triggers", [])
    status = body.get("status", "draft")
    max_concurrent_runs = body.get("max_concurrent_runs", 5)
    timeout = body.get("timeout")
    metadata = body.get("metadata", {})

    # Validate steps
    if not isinstance(steps, list):
        raise EvershadeError.validation_error("steps must be a list")
    for step in steps:
        if not isinstance(step, dict) or "step_id" not in step or "name" not in step or "type" not in step:
            raise EvershadeError.validation_error(
                "Each step must have step_id, name, and type"
            )

    await db.execute(
        """INSERT INTO workflows
           (id, name, description, steps, triggers, status, max_concurrent_runs, timeout, metadata)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            workflow_id,
            name,
            description,
            json.dumps(steps),
            json.dumps(triggers),
            status,
            max_concurrent_runs,
            timeout,
            json.dumps(metadata),
        ),
    )

    row = await db.fetchone("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
    return {
        **row,
        "steps": json.loads(row.get("steps", "[]")),
        "triggers": json.loads(row.get("triggers", "[]")),
        "metadata": json.loads(row.get("metadata", "{}")),
    }


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str) -> Dict[str, Any]:
    """Get a workflow definition."""
    row = await db.fetchone("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
    if not row:
        raise EvershadeError.not_found(f"Workflow {workflow_id} not found")
    return {
        **row,
        "steps": json.loads(row.get("steps", "[]")),
        "triggers": json.loads(row.get("triggers", "[]")),
        "metadata": json.loads(row.get("metadata", "{}")),
    }


@router.put("/{workflow_id}")
async def update_workflow(workflow_id: str, request: Request) -> Dict[str, Any]:
    """Update a workflow definition."""
    existing = await db.fetchone("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
    if not existing:
        raise EvershadeError.not_found(f"Workflow {workflow_id} not found")

    body = await request.json()
    updates = []
    values = []

    for field in ("name", "description", "steps", "triggers", "status", "max_concurrent_runs", "timeout", "metadata"):
        if field in body:
            val = body[field]
            if field in ("steps", "triggers", "metadata"):
                if isinstance(val, dict):
                    val = json.dumps(val)
                elif isinstance(val, list):
                    val = json.dumps(val)
            updates.append(f"{field} = ?")
            values.append(val)

    if updates:
        updates.append("updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')")
        values.append(workflow_id)
        await db.execute(
            f"UPDATE workflows SET {', '.join(updates)} WHERE id = ?",
            values,
        )

    row = await db.fetchone("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
    return {
        **row,
        "steps": json.loads(row.get("steps", "[]")),
        "triggers": json.loads(row.get("triggers", "[]")),
        "metadata": json.loads(row.get("metadata", "{}")),
    }


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str):
    """Delete a workflow definition."""
    existing = await db.fetchone("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
    if not existing:
        raise EvershadeError.not_found(f"Workflow {workflow_id} not found")
    await db.execute("DELETE FROM workflows WHERE id = ?", (workflow_id,))


# ─── Workflow Runs ───────────────────────────────────────────────────────────

@router.post("/{workflow_id}/run", status_code=201)
async def run_workflow(workflow_id: str, request: Request) -> Dict[str, Any]:
    """Manually trigger a workflow execution."""
    engine = request.app.state.workflow_engine

    body: Optional[Dict[str, Any]] = None
    try:
        body = await request.json()
    except Exception:
        pass

    try:
        run_id = await engine.execute_workflow(
            workflow_id=workflow_id,
            trigger_type="manual",
            trigger_data=body,
            context=body or {},
        )
        return {"run_id": run_id, "status": "pending"}
    except ValueError as e:
        raise EvershadeError.bad_request(str(e))


@router.get("/{workflow_id}/runs")
async def list_runs(
    workflow_id: str,
    request: Request,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """List runs for a workflow."""
    engine = request.app.state.workflow_engine
    runs = await engine.list_runs(workflow_id=workflow_id, status=status, limit=limit)
    return {"runs": runs, "count": len(runs)}


@router.get("/runs/{run_id}")
async def get_run_status(run_id: str, request: Request) -> Dict[str, Any]:
    """Get the status of a workflow run."""
    engine = request.app.state.workflow_engine
    status = await engine.get_run_status(run_id)
    if not status:
        raise EvershadeError.not_found(f"Run {run_id} not found")
    return status


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str, request: Request) -> Dict[str, Any]:
    """Cancel a running workflow."""
    engine = request.app.state.workflow_engine
    cancelled = await engine.cancel_run(run_id)
    if not cancelled:
        raise EvershadeError.bad_request("Cannot cancel this run")
    return {"status": "cancelled", "run_id": run_id}


# ─── Webhooks ────────────────────────────────────────────────────────────────

@router.get("/webhooks")
async def list_webhooks() -> List[Dict[str, Any]]:
    """List all webhooks."""
    rows = await db.fetchall("SELECT * FROM webhooks ORDER BY created_at DESC")
    return [{**row, "enabled": bool(row["enabled"])} for row in rows]


@router.post("/webhooks", status_code=201)
async def create_webhook(request: Request) -> Dict[str, Any]:
    """Create a new webhook."""
    body = await request.json()

    webhook_id = str(uuid.uuid4())
    name = body.get("name", "")
    workflow_id = body.get("workflow_id", "")

    if not name:
        raise EvershadeError.validation_error("name is required")
    if not workflow_id:
        raise EvershadeError.validation_error("workflow_id is required")

    # Verify workflow exists
    wf = await db.fetchone("SELECT id FROM workflows WHERE id = ?", (workflow_id,))
    if not wf:
        raise EvershadeError.not_found(f"Workflow {workflow_id} not found")

    secret = body.get("secret", "")
    if not secret:
        secret = uuid.uuid4().hex

    await db.execute(
        """INSERT INTO webhooks (id, name, workflow_id, secret)
           VALUES (?, ?, ?, ?)""",
        (webhook_id, name, workflow_id, secret),
    )

    row = await db.fetchone("SELECT * FROM webhooks WHERE id = ?", (webhook_id,))
    return {**row, "enabled": bool(row["enabled"]), "webhook_url": f"/api/workflows/webhook/{webhook_id}"}


@router.get("/webhooks/{webhook_id}")
async def get_webhook(webhook_id: str) -> Dict[str, Any]:
    """Get a webhook."""
    row = await db.fetchone("SELECT * FROM webhooks WHERE id = ?", (webhook_id,))
    if not row:
        raise EvershadeError.not_found(f"Webhook {webhook_id} not found")
    return {**row, "enabled": bool(row["enabled"]), "webhook_url": f"/api/workflows/webhook/{webhook_id}"}


@router.delete("/webhooks/{webhook_id}", status_code=204)
async def delete_webhook(webhook_id: str):
    """Delete a webhook."""
    existing = await db.fetchone("SELECT * FROM webhooks WHERE id = ?", (webhook_id,))
    if not existing:
        raise EvershadeError.not_found(f"Webhook {webhook_id} not found")
    await db.execute("DELETE FROM webhooks WHERE id = ?", (webhook_id,))


# ─── Webhook Handler (public endpoint) ───────────────────────────────────────

@router.post("/webhook/{webhook_id}")
async def handle_webhook(webhook_id: str, request: Request) -> Dict[str, Any]:
    """Handle incoming webhook events.

    This is the public endpoint that external services call to trigger workflows.
    Supports HMAC signature verification via X-Webhook-Signature header.
    """
    engine = request.app.state.workflow_engine

    # Get webhook config
    row = await db.fetchone("SELECT * FROM webhooks WHERE id = ?", (webhook_id,))
    if not row:
        raise EvershadeError.not_found("Webhook not found")
    if not row["enabled"]:
        raise EvershadeError.bad_request("Webhook is disabled")

    # Verify HMAC signature if secret is set
    secret = row.get("secret", "")
    if secret:
        signature = request.headers.get("X-Webhook-Signature", "")
        body_bytes = await request.body()
        expected = hmac.new(
            secret.encode(), body_bytes, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise EvershadeError.forbidden("Invalid webhook signature")
        payload = json.loads(body_bytes)
    else:
        payload = await request.json()

    # Trigger workflow
    run_id = await engine.handle_webhook(webhook_id, payload)

    if run_id:
        return {"status": "triggered", "run_id": run_id}
    else:
        return {"status": "failed", "message": "Failed to trigger workflow"}
