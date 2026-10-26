"""Poltergeist — Pydantic models for API request/response validation."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ─── Channels ────────────────────────────────────────────────────────────────

class ChannelType(str, Enum):
    SLACK = "slack"
    DISCORD = "discord"
    EMAIL = "email"
    TELEGRAM = "telegram"


class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(slack|discord|email|telegram)$")
    config: dict[str, Any] = Field(default_factory=dict)


class ChannelUpdate(BaseModel):
    config: Optional[dict[str, Any]] = None
    enabled: Optional[bool] = None


class ChannelResponse(BaseModel):
    id: str
    name: str
    type: str
    config: dict[str, Any]
    enabled: bool
    created_at: str


# ─── Templates ───────────────────────────────────────────────────────────────

class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    channel_type: str = Field(..., pattern="^(slack|discord|email|telegram)$")
    subject: str = ""
    body: str = Field(..., min_length=1)


class TemplateUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None


class TemplateResponse(BaseModel):
    id: str
    name: str
    channel_type: str
    subject: str
    body: str
    created_at: str


# ─── Notifications ───────────────────────────────────────────────────────────

class NotificationCreate(BaseModel):
    channel_id: str = Field(..., min_length=1)
    recipient: str = Field(..., min_length=1)
    subject: str = ""
    body: str = Field(..., min_length=1)
    template_name: str = ""
    max_retries: int = Field(3, ge=0, le=10)
    scheduled_at: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    channel_id: str
    recipient: str
    subject: str
    body: str
    status: str
    created_at: str


# ─── Delivery History ────────────────────────────────────────────────────────

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


class DeliveryHistoryResponse(BaseModel):
    id: str
    channel_id: str
    channel_type: str
    recipient: str
    subject: str
    body: str
    status: str
    error_message: str
    retry_count: int
    sent_at: str
    created_at: str
