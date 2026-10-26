"""Sneaker — Pydantic models for API request/response validation."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ─── Traces ──────────────────────────────────────────────────────────────────

class SpanKind(str, Enum):
    UNSPECIFIED = "SPAN_KIND_UNSPECIFIED"
    INTERNAL = "SPAN_KIND_INTERNAL"
    SERVER = "SPAN_KIND_SERVER"
    CLIENT = "SPAN_KIND_CLIENT"
    PRODUCER = "SPAN_KIND_PRODUCER"
    CONSUMER = "SPAN_KIND_CONSUMER"


class SpanStatus(str, Enum):
    UNSET = "UNSET"
    OK = "OK"
    ERROR = "ERROR"


class SpanCreate(BaseModel):
    trace_id: str = Field(..., min_length=1)
    span_id: str = Field(..., min_length=1)
    parent_span_id: str = ""
    service_name: str = Field(..., min_length=1)
    operation: str = Field(..., min_length=1)
    kind: str = "SPAN_KIND_UNSPECIFIED"
    status: str = "UNSET"
    start_time: int = Field(..., ge=0)
    end_time: int = Field(..., ge=0)
    duration_us: int = 0
    tags: dict[str, Any] = Field(default_factory=dict)
    events: list[Any] = Field(default_factory=list)


class SpanResponse(BaseModel):
    id: str
    trace_id: str
    span_id: str
    parent_span_id: str
    service_name: str
    operation: str
    kind: str
    status: str
    start_time: int
    end_time: int
    duration_us: int
    tags: dict[str, Any]
    events: list[Any]
    created_at: str


class TraceQuery(BaseModel):
    trace_id: Optional[str] = None
    service_name: Optional[str] = None
    operation: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# ─── Logs ────────────────────────────────────────────────────────────────────

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


class LogCreate(BaseModel):
    trace_id: str = ""
    span_id: str = ""
    service_name: str = Field(..., min_length=1)
    level: str = "info"
    message: str = Field(..., min_length=1)
    body: str = ""
    attributes: dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None


class LogResponse(BaseModel):
    id: str
    trace_id: str
    span_id: str
    service_name: str
    level: str
    message: str
    body: str
    attributes: dict[str, Any]
    timestamp: str


class LogQuery(BaseModel):
    service_name: Optional[str] = None
    level: Optional[str] = None
    trace_id: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# ─── Metrics ─────────────────────────────────────────────────────────────────

class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


class MetricCreate(BaseModel):
    name: str = Field(..., min_length=1)
    service_name: str = Field(..., min_length=1)
    metric_type: str = Field(..., pattern="^(counter|gauge|histogram)$")
    value: float
    labels: dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None


class MetricResponse(BaseModel):
    id: str
    name: str
    service_name: str
    metric_type: str
    value: float
    labels: dict[str, Any]
    timestamp: str


class MetricQuery(BaseModel):
    name: Optional[str] = None
    service_name: Optional[str] = None
    metric_type: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# ─── Alert Rules ─────────────────────────────────────────────────────────────

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertCondition(str, Enum):
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    EQ = "eq"


class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    metric_name: str = Field(..., min_length=1)
    condition: str = Field(..., pattern="^(gt|lt|gte|lte|eq)$")
    threshold: float
    window_seconds: int = Field(300, ge=10, le=86400)
    severity: str = "warning"


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metric_name: Optional[str] = None
    condition: Optional[str] = None
    threshold: Optional[float] = None
    window_seconds: Optional[int] = None
    severity: Optional[str] = None
    enabled: Optional[bool] = None


class AlertRuleResponse(BaseModel):
    id: str
    name: str
    description: str
    metric_name: str
    condition: str
    threshold: float
    window_seconds: int
    severity: str
    enabled: bool
    last_triggered: str
    created_at: str


# ─── Alert History ───────────────────────────────────────────────────────────

class AlertHistoryResponse(BaseModel):
    id: str
    rule_id: str
    metric_name: str
    value: float
    threshold: float
    severity: str
    message: str
    triggered_at: str


# ─── OTLP Ingest ─────────────────────────────────────────────────────────────

class OTLPSpan(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str = ""
    service_name: str
    operation: str
    kind: str = "SPAN_KIND_UNSPECIFIED"
    status: str = "UNSET"
    start_time: int
    end_time: int
    tags: dict[str, Any] = Field(default_factory=dict)
    events: list[Any] = Field(default_factory=list)


class OTLPTracesRequest(BaseModel):
    spans: list[OTLPSpan] = Field(default_factory=list)


class OTLPLog(BaseModel):
    trace_id: str = ""
    span_id: str = ""
    service_name: str
    level: str = "info"
    message: str
    body: str = ""
    attributes: dict[str, Any] = Field(default_factory=dict)


class OTLPLogsRequest(BaseModel):
    logs: list[OTLPLog] = Field(default_factory=list)


class OTLPMetric(BaseModel):
    name: str
    service_name: str
    metric_type: str
    value: float
    labels: dict[str, Any] = Field(default_factory=dict)


class OTLPMetricsRequest(BaseModel):
    metrics: list[OTLPMetric] = Field(default_factory=list)


class OTLPResponse(BaseModel):
    partial_success: bool = True
    error_message: str = ""
