"""Greenie — Pydantic models."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def gen_id() -> str:
    return str(uuid4())


class AgentCreate(BaseModel):
    name: str
    description: str = ""
    model: str = ""
    system_prompt: str = ""


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    model: str
    system_prompt: str
    status: str
    metadata: dict[str, Any] = {}
    created_at: str
    updated_at: str


class MissionCreate(BaseModel):
    name: str
    description: str = ""
    agent_id: str


class MissionResponse(BaseModel):
    id: str
    name: str
    description: str
    agent_id: str
    status: str
    progress: float = 0.0
    result: str = ""
    error: str = ""
    started_at: str | None = None
    completed_at: str | None = None
    created_at: str
    updated_at: str


class TaskCreate(BaseModel):
    mission_id: str
    name: str
    description: str = ""
    task_type: str = "execution"
    payload: dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    id: str
    mission_id: str
    name: str
    description: str
    type: str
    status: str
    payload: dict[str, Any] = {}
    result: str = ""
    error: str = ""
    assigned_to: str = ""
    started_at: str | None = None
    completed_at: str | None = None
    created_at: str
    updated_at: str
