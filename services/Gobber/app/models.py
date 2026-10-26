"""Gobber — Pydantic models for API request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ─── Webhooks ────────────────────────────────────────────────────────────────

class WebhookCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1)
    method: str = "POST"
    headers: dict[str, str] = Field(default_factory=dict)
    events: list[str] = Field(default_factory=list)
    secret: str = ""


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    method: Optional[str] = None
    headers: Optional[dict[str, str]] = None
    events: Optional[list[str]] = None
    enabled: Optional[bool] = None
    secret: Optional[str] = None


class WebhookResponse(BaseModel):
    id: str
    name: str
    url: str
    method: str
    headers: dict[str, str]
    events: list[str]
    enabled: bool
    created_at: str
    updated_at: str


# ─── Analytics Events ────────────────────────────────────────────────────────

class AnalyticsEventCreate(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=100)
    entity_id: str = ""
    entity_type: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)


class AnalyticsEventResponse(BaseModel):
    id: str
    event_type: str
    entity_id: str
    entity_type: str
    properties: dict[str, Any]
    created_at: str


# ─── RBAC ─────────────────────────────────────────────────────────────────────

class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    permissions: list[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[list[str]] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: str
    permissions: list[str]
    created_at: str


class UserRoleCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    role_id: str = Field(..., min_length=1)


class UserRoleResponse(BaseModel):
    id: str
    user_id: str
    role_id: str
    created_at: str


# ─── Cache ────────────────────────────────────────────────────────────────────

class CacheSet(BaseModel):
    key: str = Field(..., min_length=1)
    value: str
    ttl_seconds: int = Field(default=3600, ge=1, le=86400)


# ─── Feature Flags ────────────────────────────────────────────────────────────

class FeatureFlagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    enabled: bool = False
    config: dict[str, Any] = Field(default_factory=dict)


class FeatureFlagUpdate(BaseModel):
    enabled: Optional[bool] = None
    config: Optional[dict[str, Any]] = None


class FeatureFlagResponse(BaseModel):
    id: str
    name: str
    description: str
    enabled: bool
    config: dict[str, Any]
    created_at: str
    updated_at: str


# ─── Knowledge Graph ──────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = ""
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: list[str]
    metadata: dict[str, Any]
    created_at: str
    updated_at: str


class NoteLinkCreate(BaseModel):
    source_id: str = Field(..., min_length=1)
    target_id: str = Field(..., min_length=1)
    relation: str = "related"


class NoteLinkResponse(BaseModel):
    id: str
    source_id: str
    target_id: str
    relation: str
    created_at: str


# ─── Embeddings ───────────────────────────────────────────────────────────────

class EmbeddingCreate(BaseModel):
    texts: list[str] = Field(..., min_length=1)
    model: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingSearch(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    model: str = ""


class EmbeddingResponse(BaseModel):
    id: str
    text: str
    vector: list[float]
    model: str
    dimensions: int
    metadata: dict[str, Any]
    created_at: str


# ─── Vault ────────────────────────────────────────────────────────────────────

class VaultFileResponse(BaseModel):
    id: str
    path: str
    title: str
    content_hash: str
    tags: list[str]
    links: list[str]
    embedded: bool
    last_synced: Optional[str]
    created_at: str
    updated_at: str
