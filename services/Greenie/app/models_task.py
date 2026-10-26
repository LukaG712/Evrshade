"""Greenie — Task orchestration Pydantic models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Task Status ────────────────────────────────────────────────────────

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class SubtaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


# ── Task ───────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(default="", max_length=10000)
    agent_id: Optional[str] = None
    required_capabilities: List[str] = Field(default_factory=list)
    priority: int = Field(default=5, ge=1, le=10)
    project_id: Optional[str] = None
    mission_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    agent_id: Optional[str]
    required_capabilities: List[str] = []
    priority: int
    project_id: Optional[str]
    mission_id: Optional[str]
    status: str
    metadata: Dict[str, Any] = {}
    subtasks: List[Dict[str, Any]] = []
    created_at: str
    updated_at: str
    completed_at: Optional[str]


# ── Subtask ────────────────────────────────────────────────────────────

class SubtaskResponse(BaseModel):
    id: str
    task_id: str
    title: str
    description: str
    required_capabilities: List[str] = []
    dependency_ids: List[str] = []
    order_index: int
    status: str
    attempt: int = 0
    error: Optional[str]
    result_data: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    completed_at: Optional[str]


# ── Task Result ────────────────────────────────────────────────────────

class TaskResultResponse(BaseModel):
    id: str
    task_id: str
    subtask_id: Optional[str]
    status: str
    output: Optional[str]
    error: Optional[str]
    exit_code: int
    created_at: str


# ── Agent Capability ───────────────────────────────────────────────────

class AgentCapabilityResponse(BaseModel):
    agent_id: str
    name: str
    capabilities: List[str]
    model: str
    autonomy_level: str
    metadata: Dict[str, Any] = {}


# ── Task Actions ───────────────────────────────────────────────────────

class TaskCancelResponse(BaseModel):
    task_id: str
    cancelled: bool
    message: str


class TaskRetryResponse(BaseModel):
    task_id: str
    status: str
    message: str
