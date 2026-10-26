"""Sneaker — Alert rules management and evaluation.

Provides CRUD for alert rules and periodic evaluation against stored metrics.
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter

from evershade.errors import EvershadeError

from app.database import db
from app.models import (
    AlertHistoryResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/rules", response_model=list[AlertRuleResponse])
async def list_alert_rules():
    """List all alert rules."""
    rows = await db.fetchall("SELECT * FROM alert_rules ORDER BY created_at DESC")
    return [AlertRuleResponse(**{**row, "enabled": bool(row["enabled"])}) for row in rows]


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(rule_id: str):
    """Get a single alert rule."""
    row = await db.fetchone("SELECT * FROM alert_rules WHERE id = ?", (rule_id,))
    if not row:
        raise EvershadeError.not_found(f"Alert rule {rule_id} not found")
    return AlertRuleResponse(**{**row, "enabled": bool(row["enabled"])})


@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(rule: AlertRuleCreate):
    """Create a new alert rule."""
    rule_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO alert_rules (id, name, description, metric_name,
           condition, threshold, window_seconds, severity)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            rule_id,
            rule.name,
            rule.description,
            rule.metric_name,
            rule.condition,
            rule.threshold,
            rule.window_seconds,
            rule.severity,
        ),
    )
    row = await db.fetchone("SELECT * FROM alert_rules WHERE id = ?", (rule_id,))
    return AlertRuleResponse(**{**row, "enabled": bool(row["enabled"])})


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(rule_id: str, rule: AlertRuleUpdate):
    """Update an existing alert rule."""
    updates = rule.model_dump(exclude_none=True)
    if not updates:
        raise EvershadeError.validation_error("No fields to update")

    # Convert enabled bool to int
    if "enabled" in updates:
        updates["enabled"] = 1 if updates["enabled"] else 0

    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [rule_id]

    existing = await db.fetchone("SELECT * FROM alert_rules WHERE id = ?", (rule_id,))
    if not existing:
        raise EvershadeError.not_found(f"Alert rule {rule_id} not found")
    await db.execute(
        f"UPDATE alert_rules SET {set_clause} WHERE id = ?",
        values,
    )
    row = await db.fetchone("SELECT * FROM alert_rules WHERE id = ?", (rule_id,))
    return AlertRuleResponse(**{**row, "enabled": bool(row["enabled"])})


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_alert_rule(rule_id: str):
    """Delete an alert rule."""
    existing = await db.fetchone("SELECT * FROM alert_rules WHERE id = ?", (rule_id,))
    if not existing:
        raise EvershadeError.not_found(f"Alert rule {rule_id} not found")
    await db.execute("DELETE FROM alert_rules WHERE id = ?", (rule_id,))


@router.get("/history", response_model=list[AlertHistoryResponse])
async def list_alert_history(
    rule_id: str | None = None,
    limit: int = 100,
):
    """List alert trigger history."""
    if rule_id:
        rows = await db.fetchall(
            "SELECT * FROM alert_history WHERE rule_id = ? ORDER BY triggered_at DESC LIMIT ?",
            (rule_id, limit),
        )
    else:
        rows = await db.fetchall(
            "SELECT * FROM alert_history ORDER BY triggered_at DESC LIMIT ?",
            (limit,),
        )
    return [AlertHistoryResponse(**row) for row in rows]


@router.post("/evaluate", status_code=200)
async def evaluate_alerts():
    """Manually trigger alert evaluation against current metrics."""
    results = []

    rules = await db.fetchall("SELECT * FROM alert_rules WHERE enabled = 1")

    for rule in rules:
        metric_name = rule["metric_name"]
        window = rule["window_seconds"]
        threshold = rule["threshold"]
        condition = rule["condition"]

        # Get the latest metric value within the window
        row = await db.fetchone(
            """SELECT value FROM metrics
               WHERE name = ?
               AND timestamp >= datetime('now', ? || ' seconds')
               ORDER BY timestamp DESC LIMIT 1""",
            (metric_name, f"-{window}"),
        )

        if row is None:
            continue

        value = row["value"]
        triggered = False

        if condition == "gt" and value > threshold:
            triggered = True
        elif condition == "lt" and value < threshold:
            triggered = True
        elif condition == "gte" and value >= threshold:
            triggered = True
        elif condition == "lte" and value <= threshold:
            triggered = True
        elif condition == "eq" and value == threshold:
            triggered = True

        if triggered:
            alert_id = str(uuid.uuid4())
            message = f"Alert '{rule['name']}' triggered: {metric_name} = {value} {condition} {threshold}"
            await db.execute(
                """INSERT INTO alert_history (id, rule_id, metric_name,
                   value, threshold, severity, message)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    alert_id,
                    rule["id"],
                    metric_name,
                    value,
                    threshold,
                    rule["severity"],
                    message,
                ),
            )
            # Update last_triggered on the rule
            await db.execute(
                "UPDATE alert_rules SET last_triggered = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE id = ?",
                (rule["id"],),
            )
            results.append({
                "rule_id": rule["id"],
                "message": message,
                "value": value,
            })

    return {"evaluated": len(results), "alerts": results}
