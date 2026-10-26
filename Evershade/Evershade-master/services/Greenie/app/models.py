"""Greenie — Pydantic models for API request/response validation."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ─── Agents ──────────────────────────────────────────────────────────────────

class AutonomyLevel(str, Enum):
    SUPERVISED = "supervised"
    RESTRICTED = "restricted"
    FULL = "full"


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    model: str = "gpt-4"
    system_prompt: str = ""
    config: dict[str, Any] = Field(default_factory=dict)
    autonomy_level: AutonomyLevel = AutonomyLevel.SUPERVISED


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    autonomy_level: Optional[AutonomyLevel] = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    model: str
    system_prompt: str
    config: dict[str, Any]
    autonomy_level: str
    created_at: str
    updated_at: str


# ─── Chat Sessions ───────────────────────────────────────────────────────────

class ChatSessionStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ChatSessionCreate(BaseModel):
    agent_id: str = Field(..., min_length=1)
    user_id: str = ""
    title: str = ""


class ChatSessionResponse(BaseModel):
    id: str
    agent_id: str
    user_id: str
    title: str
    status: str
    created_at: str
    updated_at: str


# ─── Chat Messages ───────────────────────────────────────────────────────────

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ChatMessageCreate(BaseModel):
    session_id: str = Field(..., min_length=1)
    role: MessageRole
    content: str
    model: str = ""
    tool_calls: list[Any] = Field(default_factory=list)
    token_count: int = 0


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    model: str
    tool_calls: list[Any]
    token_count: int
    created_at: str


# ─── Missions ────────────────────────────────────────────────────────────────

class MissionStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MissionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    agent_id: str = Field(..., min_length=1)
    autonomy_level: AutonomyLevel = AutonomyLevel.SUPERVISED


class MissionUpdate(BaseModel):
    status: Optional[MissionStatus] = None
    current_milestone: Optional[str] = None
    progress_percent: Optional[int] = Field(None, ge=0, le=100)


class MissionResponse(BaseModel):
    id: str
    name: str
    description: str
    agent_id: str
    status: str
    autonomy_level: str
    current_milestone: str
    progress_percent: int
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: str
    updated_at: str


# ─── Milestones ──────────────────────────────────────────────────────────────

class MilestoneStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class MilestoneCreate(BaseModel):
    mission_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    order_index: int = 0


class MilestoneResponse(BaseModel):
    id: str
    mission_id: str
    name: str
    description: str
    status: str
    order_index: int
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: str


# ─── Features ────────────────────────────────────────────────────────────────

class FeatureCreate(BaseModel):
    milestone_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    order_index: int = 0


class FeatureResponse(BaseModel):
    id: str
    milestone_id: str
    name: str
    description: str
    status: str
    order_index: int
    created_at: str


# ─── Validation Contracts ────────────────────────────────────────────────────

class ValidationContractCreate(BaseModel):
    milestone_id: str = Field(..., min_length=1)
    criterion: str = Field(..., min_length=1)


class ValidationContractResponse(BaseModel):
    id: str
    milestone_id: str
    criterion: str
    status: str
    result: str
    created_at: str


# ─── Checkpoints ─────────────────────────────────────────────────────────────

class CheckpointCreate(BaseModel):
    mission_id: str = Field(..., min_length=1)
    state: dict[str, Any] = Field(default_factory=dict)
    milestone_id: str = ""


class CheckpointResponse(BaseModel):
    id: str
    mission_id: str
    state: dict[str, Any]
    milestone_id: str
    created_at: str


# ─── Approval Gates ──────────────────────────────────────────────────────────

class ApprovalGateCreate(BaseModel):
    mission_id: str = Field(..., min_length=1)
    request: str = Field(..., min_length=1)
    milestone_id: str = ""


class ApprovalGateResponse(BaseModel):
    id: str
    mission_id: str
    milestone_id: str
    request: str
    status: str
    response: str
    created_at: str
    resolved_at: Optional[str]


# ─── Specs ───────────────────────────────────────────────────────────────────

class SpecStatus(str, Enum):
    DRAFT = "draft"
    RESEARCHING = "researching"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED = "converted"


class SpecCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""


class SpecUpdate(BaseModel):
    status: Optional[SpecStatus] = None
    research_notes: Optional[str] = None


class SpecResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    research_notes: str
    converted_mission_id: str
    created_at: str
    updated_at: str


# ─── Droids ──────────────────────────────────────────────────────────────────

class DroidCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    trigger_phrases: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)
    source: str = ""


class DroidResponse(BaseModel):
    id: str
    name: str
    description: str
    trigger_phrases: list[str]
    config: dict[str, Any]
    source: str
    enabled: bool
    created_at: str


# ─── Skills ──────────────────────────────────────────────────────────────────

class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    trigger_phrases: list[str] = Field(default_factory=list)
    steps: list[Any] = Field(default_factory=list)


class SkillResponse(BaseModel):
    id: str
    name: str
    description: str
    trigger_phrases: list[str]
    steps: list[Any]
    enabled: bool
    created_at: str


# ─── Hooks ───────────────────────────────────────────────────────────────────

class HookCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    event: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    config: dict[str, Any] = Field(default_factory=dict)


class HookResponse(BaseModel):
    id: str
    name: str
    event: str
    action: str
    config: dict[str, Any]
    enabled: bool
    created_at: str


# ─── Environments ────────────────────────────────────────────────────────────

class EnvironmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    config: dict[str, Any] = Field(default_factory=dict)


class EnvironmentResponse(BaseModel):
    id: str
    name: str
    description: str
    config: dict[str, Any]
    validated: bool
    created_at: str


# ─── Users ───────────────────────────────────────────────────────────────────

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: str = ""
    role: UserRole = UserRole.USER


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: str


# ─── Mission Logs ────────────────────────────────────────────────────────────

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


class MissionLogCreate(BaseModel):
    mission_id: str = Field(..., min_length=1)
    level: LogLevel = LogLevel.INFO
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class MissionLogResponse(BaseModel):
    id: str
    mission_id: str
    level: str
    message: str
    data: dict[str, Any]
    created_at: str


# ─── Chat Completion (OpenAI-compatible) ─────────────────────────────────────

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


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: list[dict[str, Any]]
