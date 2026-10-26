"""Hider — Pydantic models for API request/response validation."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─── Secrets ─────────────────────────────────────────────────────────────────

class SecretCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=200)
    value: str = Field(..., min_length=1)
    description: str = ""


class SecretResponse(BaseModel):
    id: str
    key: str
    value: str
    description: str
    created_at: str
    updated_at: str


class SecretUpdate(BaseModel):
    value: str = Field(..., min_length=1)
    description: Optional[str] = None


# ─── Configuration ───────────────────────────────────────────────────────────

class ConfigCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=200)
    value: str = Field(..., min_length=1)
    description: str = ""


class ConfigUpdate(BaseModel):
    value: str = Field(..., min_length=1)
    description: Optional[str] = None


class ConfigResponse(BaseModel):
    id: str
    key: str
    value: str
    version: int
    description: str
    created_at: str
    updated_at: str


class ConfigHistoryResponse(BaseModel):
    id: str
    key: str
    value: str
    version: int
    changed_by: str
    changed_at: str


# ─── Audit Log ───────────────────────────────────────────────────────────────

class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class AuditLogResponse(BaseModel):
    id: str
    secret_key: str
    action: str
    actor: str
    ip_address: str
    success: bool
    details: str
    created_at: str
