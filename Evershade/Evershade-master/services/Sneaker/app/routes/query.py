"""Sneaker — Query endpoints for traces, logs, and metrics.

Provides RESTful query interfaces for searching and retrieving stored telemetry data.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Query

from app.database import db
from app.models import (
    LogResponse,
    LogQuery,
    MetricQuery,
    MetricResponse,
    SpanResponse,
    TraceQuery,
)

router = APIRouter(prefix="/api", tags=["query"])


# ─── Traces ──────────────────────────────────────────────────────────────────

@router.get("/traces", response_model=list[SpanResponse])
async def list_traces(
    service_name: str | None = None,
    status: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List trace spans with optional filters."""
    conditions = []
    params = []

    if service_name:
        conditions.append("service_name = ?")
        params.append(service_name)
    if status:
        conditions.append("status = ?")
        params.append(status)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    params.extend([limit, offset])

    rows = await db.fetchall(
        f"SELECT * FROM traces {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params,
    )
    for row in rows:
        row["tags"] = json.loads(row.get("tags", "{}"))
        row["events"] = json.loads(row.get("events", "[]"))
    return [SpanResponse(**row) for row in rows]


@router.get("/traces/{trace_id}", response_model=list[SpanResponse])
async def get_trace(trace_id: str):
    """Get all spans for a specific trace."""
    rows = await db.fetchall(
        "SELECT * FROM traces WHERE trace_id = ? ORDER BY start_time ASC",
        (trace_id,),
    )
    for row in rows:
        row["tags"] = json.loads(row.get("tags", "{}"))
        row["events"] = json.loads(row.get("events", "[]"))
    return [SpanResponse(**row) for row in rows]


# ─── Logs ────────────────────────────────────────────────────────────────────

@router.get("/logs", response_model=list[LogResponse])
async def list_logs(
    service_name: str | None = None,
    level: str | None = None,
    trace_id: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List log entries with optional filters."""
    conditions = []
    params = []

    if service_name:
        conditions.append("service_name = ?")
        params.append(service_name)
    if level:
        conditions.append("level = ?")
        params.append(level)
    if trace_id:
        conditions.append("trace_id = ?")
        params.append(trace_id)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    params.extend([limit, offset])

    rows = await db.fetchall(
        f"SELECT * FROM logs {where} ORDER BY timestamp DESC LIMIT ? OFFSET ?",
        params,
    )
    for row in rows:
        row["attributes"] = json.loads(row.get("attributes", "{}"))
    return [LogResponse(**row) for row in rows]


# ─── Metrics ─────────────────────────────────────────────────────────────────

@router.get("/metrics", response_model=list[MetricResponse])
async def list_metrics(
    name: str | None = None,
    service_name: str | None = None,
    metric_type: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List metric data points with optional filters."""
    conditions = []
    params = []

    if name:
        conditions.append("name = ?")
        params.append(name)
    if service_name:
        conditions.append("service_name = ?")
        params.append(service_name)
    if metric_type:
        conditions.append("metric_type = ?")
        params.append(metric_type)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    params.extend([limit, offset])

    rows = await db.fetchall(
        f"SELECT * FROM metrics {where} ORDER BY timestamp DESC LIMIT ? OFFSET ?",
        params,
    )
    for row in rows:
        row["labels"] = json.loads(row.get("labels", "{}"))
    return [MetricResponse(**row) for row in rows]


@router.post("/traces/search", response_model=list[SpanResponse])
async def search_traces(query: TraceQuery):
    """Search traces with structured query."""
    conditions = []
    params = []

    if query.trace_id:
        conditions.append("trace_id = ?")
        params.append(query.trace_id)
    if query.service_name:
        conditions.append("service_name = ?")
        params.append(query.service_name)
    if query.operation:
        conditions.append("operation LIKE ?")
        params.append(f"%{query.operation}%")
    if query.status:
        conditions.append("status = ?")
        params.append(query.status)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    params.extend([query.limit, query.offset])

    rows = await db.fetchall(
        f"SELECT * FROM traces {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params,
    )
    for row in rows:
        row["tags"] = json.loads(row.get("tags", "{}"))
        row["events"] = json.loads(row.get("events", "[]"))
    return [SpanResponse(**row) for row in rows]


@router.post("/logs/search", response_model=list[LogResponse])
async def search_logs(query: LogQuery):
    """Search logs with structured query."""
    conditions = []
    params = []

    if query.service_name:
        conditions.append("service_name = ?")
        params.append(query.service_name)
    if query.level:
        conditions.append("level = ?")
        params.append(query.level)
    if query.trace_id:
        conditions.append("trace_id = ?")
        params.append(query.trace_id)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    params.extend([query.limit, query.offset])

    rows = await db.fetchall(
        f"SELECT * FROM logs {where} ORDER BY timestamp DESC LIMIT ? OFFSET ?",
        params,
    )
    for row in rows:
        row["attributes"] = json.loads(row.get("attributes", "{}"))
    return [LogResponse(**row) for row in rows]


@router.post("/metrics/search", response_model=list[MetricResponse])
async def search_metrics(query: MetricQuery):
    """Search metrics with structured query."""
    conditions = []
    params = []

    if query.name:
        conditions.append("name = ?")
        params.append(query.name)
    if query.service_name:
        conditions.append("service_name = ?")
        params.append(query.service_name)
    if query.metric_type:
        conditions.append("metric_type = ?")
        params.append(query.metric_type)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    params.extend([query.limit, query.offset])

    rows = await db.fetchall(
        f"SELECT * FROM metrics {where} ORDER BY timestamp DESC LIMIT ? OFFSET ?",
        params,
    )
    for row in rows:
        row["labels"] = json.loads(row.get("labels", "{}"))
    return [MetricResponse(**row) for row in rows]
