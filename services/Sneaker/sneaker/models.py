"""Data models for Sneaker observability service."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


class MetricPoint:
    def __init__(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
        timestamp: datetime | None = None,
        id: UUID | None = None,
    ):
        self.id = id or uuid4()
        self.name = name
        self.value = value
        self.labels = labels or {}
        self.timestamp = timestamp or datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        ts = self.timestamp
        if isinstance(ts, str):
            ts_str = ts
        else:
            ts_str = ts.isoformat()
        return {
            "id": str(self.id),
            "name": self.name,
            "value": self.value,
            "labels": self.labels,
            "timestamp": ts_str,
        }


class TraceSpan:
    def __init__(
        self,
        trace_id: str,
        operation: str,
        duration_ms: float,
        service: str | None = None,
        parent_id: str | None = None,
        span_id: str | None = None,
        status: str | None = None,
        attributes: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ):
        self.span_id = span_id or str(uuid4())
        self.trace_id = trace_id
        self.operation = operation
        self.duration_ms = duration_ms
        self.service = service
        self.parent_id = parent_id
        self.status = status
        self.attributes = attributes or {}
        self.timestamp = timestamp or datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        ts = self.timestamp
        if isinstance(ts, str):
            ts_str = ts
        else:
            ts_str = ts.isoformat()
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            "service": self.service,
            "parent_id": self.parent_id,
            "status": self.status,
            "attributes": self.attributes,
            "timestamp": ts_str,
        }


class LogEntry:
    def __init__(
        self,
        level: str,
        message: str,
        service: str | None = None,
        metadata: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
        id: UUID | None = None,
    ):
        self.id = id or uuid4()
        self.level = level.upper()
        self.message = message
        self.service = service
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        ts = self.timestamp
        if isinstance(ts, str):
            ts_str = ts
        else:
            ts_str = ts.isoformat()
        return {
            "id": str(self.id),
            "level": self.level,
            "message": self.message,
            "service": self.service,
            "metadata": self.metadata,
            "timestamp": ts_str,
        }
