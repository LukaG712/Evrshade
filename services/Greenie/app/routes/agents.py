"""Greenie — Agent management routes.

CRUD operations for agent definitions and configuration.
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, HTTPException

from evershade.errors import ErrorCode, EvershadeError

from app.database import get_db_instance
from app.models import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
)

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=list[AgentResponse])
async def list_agents():
    """List all agents."""
    db = await get_db_instance()
    rows = await db.fetchall("SELECT * FROM agents ORDER BY created_at DESC")
    return [AgentResponse(**row) for row in rows]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a single agent by ID."""
    db = await get_db_instance()
    row = await db.fetchone("SELECT * FROM agents WHERE id = ?", (agent_id,))
    if not row:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Agent {agent_id} not found")
    return AgentResponse(**row)


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(agent: AgentCreate):
    """Create a new agent."""
    agent_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        """INSERT INTO agents (id, name, description, model, system_prompt, config, autonomy_level)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            agent_id,
            agent.name,
            agent.description,
            agent.model,
            agent.system_prompt,
            json.dumps(agent.config),
            agent.autonomy_level.value,
        ),
    )
    row = await db.fetchone("SELECT * FROM agents WHERE id = ?", (agent_id,))
    return AgentResponse(**row)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent: AgentUpdate):
    """Update an existing agent."""
    updates = agent.model_dump(exclude_none=True)
    if not updates:
        raise EvershadeError(ErrorCode.VALIDATION_ERROR, "No fields to update")

    # Convert enum values
    if "autonomy_level" in updates and hasattr(updates["autonomy_level"], "value"):
        updates["autonomy_level"] = updates["autonomy_level"].value
    if "config" in updates:
        updates["config"] = json.dumps(updates["config"])

    # Always update the timestamp
    updates["updated_at"] = "strftime('%Y-%m-%dT%H:%M:%SZ', 'now')"

    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [agent_id]

    db = await get_db_instance()
    row = await db.fetchone("SELECT * FROM agents WHERE id = ?", (agent_id,))
    if not row:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Agent {agent_id} not found")
    await db.execute(
        f"UPDATE agents SET {set_clause} WHERE id = ?",
        values,
    )
    row = await db.fetchone("SELECT * FROM agents WHERE id = ?", (agent_id,))
    return AgentResponse(**row)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str):
    """Delete an agent."""
    db = await get_db_instance()
    row = await db.fetchone("SELECT * FROM agents WHERE id = ?", (agent_id,))
    if not row:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Agent {agent_id} not found")
    await db.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
