"""Hider — Pydantic models."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel


def gen_id() -> str:
    return str(uuid4())


class SecretCreate(BaseModel):
    name: str
    value: str
    description: str = ""


class SecretResponse(BaseModel):
    id: str
    name: str
    description: str
    version: int
    created_at: str
    updated_at: str


class SecretUpdate(BaseModel):
    value: str


class ConfigCreate(BaseModel):
    key: str
    value: str
    is_encrypted: bool = False
    description: str = ""


class ConfigResponse(BaseModel):
    id: str
    key: str
    value: str
    is_encrypted: bool
    description: str
    version: int
    created_at: str
    updated_at: str


class AuditLogEntry(BaseModel):
    id: str
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, Any] = {}
    created_at: str
