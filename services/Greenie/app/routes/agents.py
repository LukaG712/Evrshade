"""Greenie — Agent management routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.database import db
from app.models import AgentCreate, AgentResponse, gen_id

router = APIRouter()


@router.post("/", status_code=201)
async def create_agent(agent: AgentCreate) -> AgentResponse:
    """Create a new agent."""
    aid = gen_id()
    await db.execute(
        "INSERT INTO agents (id, name, description, model, system_prompt) VALUES (?, ?, ?, ?, ?)",
        (aid, agent.name, agent.description, agent.model, agent.system_prompt),
    )
    row = await db.fetchone("SELECT * FROM agents WHERE id = ?", (aid,))
    return AgentResponse(**row)


@router.get("/")
async def list_agents() -> list[AgentResponse]:
    """List all agents."""
    rows = await db.fetchall("SELECT * FROM agents ORDER BY created_at DESC")
    return [AgentResponse(**r) for r in rows]


@router.get("/{agent_id}")
async def get_agent(agent_id: str) -> AgentResponse:
    """Get an agent by ID."""
    row = await db.fetchone("SELECT * FROM agents WHERE id = ?", (agent_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(**row)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str) -> None:
    """Delete an agent."""
    cursor = await db.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
