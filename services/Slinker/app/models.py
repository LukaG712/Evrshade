"""Slinker — Pydantic models for API request/response validation."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ─── Tasks ───────────────────────────────────────────────────────────────────

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    project_id: str = ""
    command: str = ""


class TaskResponse(BaseModel):
    id: str
    name: str
    description: str
    project_id: str
    status: str
    worktree_path: str
    command: str
    output: str
    error: str
    exit_code: Optional[int]
    worker_id: str
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: str
    updated_at: str


# ─── Workers ─────────────────────────────────────────────────────────────────

class WorkerStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    STOPPED = "stopped"


class WorkerResponse(BaseModel):
    id: str
    name: str
    status: str
    current_task_id: str
    last_heartbeat: Optional[str]
    created_at: str


# ─── Projects ────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    repo_url: str = ""
    branch: str = "main"
    worktree_base: str = ""


class ProjectResponse(BaseModel):
    id: str
    name: str
    repo_url: str
    branch: str
    worktree_base: str
    created_at: str


# ─── Sessions ────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class SessionResponse(BaseModel):
    id: str
    name: str
    status: str
    task_count: int
    started_at: str
    completed_at: Optional[str]


# ─── Session Logs ────────────────────────────────────────────────────────────

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


class SessionLogCreate(BaseModel):
    session_id: str = Field(..., min_length=1)
    task_id: str = ""
    level: LogLevel = LogLevel.INFO
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class SessionLogResponse(BaseModel):
    id: str
    session_id: str
    task_id: str
    level: str
    message: str
    data: dict[str, Any]
    created_at: str


# ─── OpenAI-compatible ───────────────────────────────────────────────────────

class ChatCompletionMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4"
    messages: list[ChatCompletionMessage]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: str = "stop"


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "slinker"
