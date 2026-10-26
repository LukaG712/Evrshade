"""Sneaker — OTLP ingest endpoints.

Accepts traces, logs, and metrics via simplified OTLP-compatible JSON endpoints.
These endpoints store data in SQLite for later querying.
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter

from app.database import db
from app.models import (
    OTLPLogsRequest,
    OTLPMetricsRequest,
    OTLPResponse,
    OTLPTracesRequest,
)

router = APIRouter(prefix="/v1", tags=["otlp"])


@router.post("/traces", response_model=OTLPResponse)
async def ingest_traces(req: OTLPTracesRequest):
    """Ingest a batch of trace spans."""
    inserted = 0
    errors = []

    for span in req.spans:
        try:
            span_id = str(uuid.uuid4())
            duration_us = max(0, span.end_time - span.start_time)
            await db.execute(
                """INSERT INTO traces (id, trace_id, span_id, parent_span_id,
                   service_name, operation, kind, status, start_time, end_time,
                   duration_us, tags, events)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    span_id,
                    span.trace_id,
                    span.span_id,
                    span.parent_span_id,
                    span.service_name,
                    span.operation,
                    span.kind,
                    span.status,
                    span.start_time,
                    span.end_time,
                    duration_us,
                    json.dumps(span.tags),
                    json.dumps(span.events),
                ),
            )
            inserted += 1
        except Exception as e:
            errors.append(str(e))

    return OTLPResponse(
        partial_success=len(errors) == 0,
        error_message=f"Failed {len(errors)} spans" if errors else "",
    )


@router.post("/logs", response_model=OTLPResponse)
async def ingest_logs(req: OTLPLogsRequest):
    """Ingest a batch of log entries."""
    inserted = 0
    errors = []

    for log in req.logs:
        try:
            log_id = str(uuid.uuid4())
            await db.execute(
                """INSERT INTO logs (id, trace_id, span_id, service_name,
                   level, message, body, attributes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    log_id,
                    log.trace_id,
                    log.span_id,
                    log.service_name,
                    log.level,
                    log.message,
                    log.body,
                    json.dumps(log.attributes),
                ),
            )
            inserted += 1
        except Exception as e:
            errors.append(str(e))

    return OTLPResponse(
        partial_success=len(errors) == 0,
        error_message=f"Failed {len(errors)} logs" if errors else "",
    )


@router.post("/metrics", response_model=OTLPResponse)
async def ingest_metrics(req: OTLPMetricsRequest):
    """Ingest a batch of metric data points."""
    inserted = 0
    errors = []

    for metric in req.metrics:
        try:
            metric_id = str(uuid.uuid4())
            await db.execute(
                """INSERT INTO metrics (id, name, service_name, metric_type,
                   value, labels)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    metric_id,
                    metric.name,
                    metric.service_name,
                    metric.metric_type,
                    metric.value,
                    json.dumps(metric.labels),
                ),
            )
            inserted += 1
        except Exception as e:
            errors.append(str(e))

    return OTLPResponse(
        partial_success=len(errors) == 0,
        error_message=f"Failed {len(errors)} metrics" if errors else "",
    )
