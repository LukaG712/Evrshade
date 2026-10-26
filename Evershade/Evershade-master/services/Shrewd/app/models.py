"""Shrewd — Pydantic models for API request/response validation."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# ─── Providers ────────────────────────────────────────────────────────────────

class ProviderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    base_url: str = ""
    api_key: str = ""
    config: dict[str, Any] = Field(default_factory=dict)


class ProviderUpdate(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    enabled: Optional[bool] = None
    config: Optional[dict[str, Any]] = None


class ProviderResponse(BaseModel):
    id: str
    name: str
    base_url: str
    enabled: bool
    created_at: str
    updated_at: str


# ─── Models ───────────────────────────────────────────────────────────────────

class ModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    provider_id: str = Field(..., min_length=1)
    context_window: int = 8192
    max_tokens: int = 4096
    supports_vision: bool = False
    supports_tools: bool = False
    supports_embeddings: bool = False
    input_cost_per_token: float = 0.0
    output_cost_per_token: float = 0.0
    config: dict[str, Any] = Field(default_factory=dict)


class ModelUpdate(BaseModel):
    context_window: Optional[int] = None
    max_tokens: Optional[int] = None
    supports_vision: Optional[bool] = None
    supports_tools: Optional[bool] = None
    supports_embeddings: Optional[bool] = None
    input_cost_per_token: Optional[float] = None
    output_cost_per_token: Optional[float] = None
    enabled: Optional[bool] = None
    config: Optional[dict[str, Any]] = None


class ModelResponse(BaseModel):
    id: str
    name: str
    provider_id: str
    context_window: int
    max_tokens: int
    supports_vision: bool
    supports_tools: bool
    supports_embeddings: bool
    input_cost_per_token: float
    output_cost_per_token: float
    enabled: bool
    created_at: str
    updated_at: str


# ─── Chat Completions ─────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant|tool)$")
    content: str


class ChatCompletionCreate(BaseModel):
    model: str = Field(..., min_length=1)
    messages: list[ChatMessage] = Field(..., min_length=1)
    temperature: float = 1.0
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    stream: bool = False
    user_id: str = ""
    privacy_level: str = "standard"


class ChatCompletionResponse(BaseModel):
    id: str
    model: str
    choices: list[dict[str, Any]]
    usage: dict[str, int]


# ─── Usage ────────────────────────────────────────────────────────────────────

class UsageRecord(BaseModel):
    id: str
    model_id: str
    provider_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    duration_ms: int
    status: str
    created_at: str


# ─── Routing Rules ────────────────────────────────────────────────────────────

class RoutingRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    priority: int = 0
    condition: dict[str, Any] = Field(default_factory=dict)
    target_model_id: str = Field(..., min_length=1)


class RoutingRuleResponse(BaseModel):
    id: str
    name: str
    priority: int
    condition: dict[str, Any]
    target_model_id: str
    enabled: bool
    created_at: str


# ─── Privacy Rules ────────────────────────────────────────────────────────────

class PrivacyRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level: str = Field(..., pattern="^(public|standard|confidential|restricted)$")
    allowed_providers: list[str] = Field(default_factory=list)
    description: str = ""


class PrivacyRuleResponse(BaseModel):
    id: str
    name: str
    level: str
    allowed_providers: list[str]
    description: str
    created_at: str
