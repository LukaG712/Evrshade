"""FastAPI application for Sneaker observability service."""

import hmac
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.middleware.cors import CORSMiddleware

from sneaker import otlp_export
from sneaker.models import LogEntry, MetricPoint, TraceSpan

app = FastAPI(
    title="Sneaker",
    description="Observability service for the Evershade ecosystem",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_api_key_raw = os.getenv("API_KEY")
if not _api_key_raw:
    raise RuntimeError(
        "API_KEY environment variable is not set. Refusing to start Sneaker without a configured API key."
    )
API_KEY = _api_key_raw
DB_PATH = os.getenv("DB_PATH", "/app/data/sneaker.db")


# SQLite persistent storage
@contextmanager
def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _init_db():
    # Use Path for safe directory creation (handles edge cases with relative paths)
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with _get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                labels TEXT DEFAULT '{}',
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                span_id TEXT NOT NULL,
                parent_span_id TEXT,
                name TEXT NOT NULL,
                duration_ms REAL,
                status TEXT,
                attributes TEXT DEFAULT '{}',
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                service TEXT,
                attributes TEXT DEFAULT '{}',
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()


_init_db()

# In-memory storage (backed by SQLite for persistence)
# Max size limit to prevent unbounded memory growth
_MAX_METRICS = 10000
_MAX_TRACES = 10000
_MAX_LOGS = 10000

_metrics: list[MetricPoint] = []
_traces: list[TraceSpan] = []
_logs: list[LogEntry] = []


def _safe_json_loads(value, default=None):
    """Safely parse JSON, returning default on failure instead of crashing."""
    if not value:
        return default if default is not None else {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


# Load persisted data from SQLite into memory on startup
def _load_from_db():
    """Load previously stored data from SQLite into in-memory lists."""
    with _get_db() as conn:
        # Load metrics
        for row in conn.execute("SELECT name, value, labels, timestamp FROM metrics ORDER BY id"):
            _metrics.append(
                MetricPoint(
                    name=row[0],
                    value=row[1],
                    labels=_safe_json_loads(row[2]),
                    timestamp=row[3],
                )
            )
        # Load traces
        for row in conn.execute(
            "SELECT trace_id, span_id, parent_span_id, name, duration_ms, status, attributes, timestamp FROM traces ORDER BY id"
        ):
            _traces.append(
                TraceSpan(
                    trace_id=row[0],
                    span_id=row[1],
                    parent_id=row[2],
                    operation=row[3],
                    duration_ms=row[4] or 0,
                    status=row[5],
                    attributes=_safe_json_loads(row[6]),
                    timestamp=row[7],
                )
            )
        # Load logs
        for row in conn.execute("SELECT level, message, service, attributes, timestamp FROM logs ORDER BY id"):
            _logs.append(
                LogEntry(
                    level=row[0],
                    message=row[1],
                    service=row[2],
                    metadata=_safe_json_loads(row[3]),
                    timestamp=row[4],
                )
            )


_load_from_db()

# Register stores with OTLP export module
otlp_export.register_stores(_metrics, _traces, _logs)

# Register OTLP routes
otlp_export.register_otlp_routes(app)

# ─── Prometheus Metrics ─────────────────────────────────────────

sneaker_http_requests_total = Counter(
    "sneaker_http_requests_total",
    "Total HTTP requests to Sneaker",
    ["method", "endpoint", "status"],
)

sneaker_http_request_duration = Histogram(
    "sneaker_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

sneaker_metrics_count = Gauge(
    "sneaker_metrics_count",
    "Number of metrics stored in Sneaker",
)

sneaker_traces_count = Gauge(
    "sneaker_traces_count",
    "Number of trace spans stored in Sneaker",
)

sneaker_logs_count = Gauge(
    "sneaker_logs_count",
    "Number of log entries stored in Sneaker",
)

sneaker_otlp_received_total = Counter(
    "sneaker_otlp_received_total",
    "Total OTLP data points received",
    ["type"],
)


@app.middleware("http")
async def prometheus_middleware(request, call_next):
    """Record Prometheus metrics for every request."""
    if request.url.path == "/metrics":
        return await call_next(request)
    method = request.method
    endpoint = request.url.path
    start = time.time()
    status = "200"
    response = None
    try:
        response = await call_next(request)
        status = str(response.status_code)
        return response
    except Exception:
        status = "500"
        raise
    finally:
        duration = time.time() - start
        sneaker_http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        sneaker_http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint for Grafana scraping."""
    # Update gauges
    sneaker_metrics_count.set(len(_metrics))
    sneaker_traces_count.set(len(_traces))
    sneaker_logs_count.set(len(_logs))
    return Response(
        content=generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )


def verify_bearer(authorization: str | None = Header(None)) -> None:
    """Verify Bearer token in Authorization header."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header. Use: Authorization: Bearer <key>",
        )
    if not hmac.compare_digest(token, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "Sneaker"}


@app.get("/api/capabilities")
async def capabilities() -> dict:
    """Return service identification, version, and features."""
    return {
        "service": "Sneaker",
        "version": "1.1.0",
        "features": [
            "metrics",
            "traces",
            "logs",
            "otlp_ingest",
            "alerting",
            "prometheus_export",
            "opentelemetry",
        ],
    }


# ─── Metrics ────────────────────────────────────────────────────


@app.post("/api/metrics")
async def record_metric(data: dict[str, Any], authorization: str | None = Header(None)) -> dict[str, Any]:
    verify_bearer(authorization)
    metric = MetricPoint(name=data["name"], value=float(data["value"]), labels=data.get("labels"))
    _metrics.append(metric)
    # Evict oldest entries if over max size
    if len(_metrics) > _MAX_METRICS:
        _metrics[: len(_metrics) - _MAX_METRICS] = []
    # Persist to SQLite
    with _get_db() as conn:
        conn.execute(
            "INSERT INTO metrics (name, value, labels, timestamp) VALUES (?, ?, ?, ?)",
            (
                metric.name,
                metric.value,
                json.dumps(metric.labels or {}),
                metric.timestamp,
            ),
        )
        conn.commit()
    return metric.to_dict()


@app.get("/api/metrics")
async def query_metrics(
    name: str | None = None,
    limit: int = 100,
    authorization: str | None = Header(None),
) -> list[dict[str, Any]]:
    verify_bearer(authorization)
    results = _metrics
    if name:
        results = [m for m in results if m.name == name]
    return [m.to_dict() for m in results[-limit:]]


@app.get("/api/metrics/summary")
async def metrics_summary(authorization: str | None = Header(None)) -> dict[str, Any]:
    """Return a summary of key metrics including latency percentiles and error counts.

    This endpoint provides aggregated metrics for dashboards and monitoring:
    - Request latency percentiles (p50, p95, p99) from trace durations
    - Error counts by service from logs
    - Queue depth (pending traces, metrics, logs)
    - Task duration statistics
    """
    verify_bearer(authorization)

    # Calculate latency percentiles from traces
    durations = [t.duration_ms for t in _traces if t.duration_ms > 0]
    durations.sort()
    n = len(durations)

    def percentile(data, p):
        if not data:
            return 0.0
        k = (len(data) - 1) * (p / 100.0)
        f = int(k)
        c = f + 1 if f + 1 < len(data) else f
        d = k - f
        return data[f] + d * (data[c] - data[f])

    # Count errors by service from logs
    errors_by_service = {}
    for entry in _logs:
        if entry.level in ("ERROR", "CRITICAL"):
            svc = entry.service or "unknown"
            errors_by_service[svc] = errors_by_service.get(svc, 0) + 1

    # Queue depths
    queue_depth = {
        "pending_traces": len(_traces),
        "pending_metrics": len(_metrics),
        "pending_logs": len(_logs),
    }

    return {
        "latency": {
            "p50_ms": round(percentile(durations, 50), 2),
            "p95_ms": round(percentile(durations, 95), 2),
            "p99_ms": round(percentile(durations, 99), 2),
            "min_ms": round(durations[0], 2) if durations else 0,
            "max_ms": round(durations[-1], 2) if durations else 0,
            "count": n,
        },
        "errors": {
            "total": sum(errors_by_service.values()),
            "by_service": errors_by_service,
        },
        "queue_depth": queue_depth,
        "task_duration": {
            "avg_ms": round(sum(durations) / n, 2) if n > 0 else 0,
            "total_traces": len(_traces),
        },
    }


# ─── Traces ─────────────────────────────────────────────────────


@app.post("/api/traces")
async def record_trace(data: dict[str, Any], authorization: str | None = Header(None)) -> dict[str, Any]:
    verify_bearer(authorization)
    span = TraceSpan(
        trace_id=data["trace_id"],
        operation=data["operation"],
        duration_ms=float(data.get("duration_ms", 0)),
        service=data.get("service"),
        parent_id=data.get("parent_id"),
        status=data.get("status"),
        attributes=data.get("attributes"),
    )
    _traces.append(span)
    # Evict oldest entries if over max size
    if len(_traces) > _MAX_TRACES:
        _traces[: len(_traces) - _MAX_TRACES] = []
    # Persist to SQLite
    with _get_db() as conn:
        conn.execute(
            "INSERT INTO traces (trace_id, span_id, parent_span_id, name, duration_ms, status, attributes, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                span.trace_id,
                span.span_id,
                span.parent_id,
                span.operation,
                span.duration_ms,
                span.status or "",
                json.dumps(span.attributes or {}),
                span.timestamp,
            ),
        )
        conn.commit()
    return span.to_dict()


@app.get("/api/traces")
async def query_traces(
    trace_id: str | None = None,
    service: str | None = None,
    limit: int = 100,
    authorization: str | None = Header(None),
) -> list[dict[str, Any]]:
    verify_bearer(authorization)
    results = _traces
    if trace_id:
        results = [t for t in results if t.trace_id == trace_id]
    if service:
        results = [t for t in results if t.service == service]
    return [t.to_dict() for t in results[-limit:]]


# ─── Logs ───────────────────────────────────────────────────────


@app.post("/api/logs")
async def record_log(data: dict[str, Any], authorization: str | None = Header(None)) -> dict[str, Any]:
    verify_bearer(authorization)
    entry = LogEntry(
        level=data["level"],
        message=data["message"],
        service=data.get("service"),
        metadata=data.get("metadata"),
    )
    _logs.append(entry)
    # Evict oldest entries if over max size
    if len(_logs) > _MAX_LOGS:
        _logs[: len(_logs) - _MAX_LOGS] = []
    # Persist to SQLite
    with _get_db() as conn:
        conn.execute(
            "INSERT INTO logs (level, message, service, attributes, timestamp) VALUES (?, ?, ?, ?, ?)",
            (
                entry.level,
                entry.message,
                entry.service,
                json.dumps(entry.metadata or {}),
                entry.timestamp,
            ),
        )
        conn.commit()
    return entry.to_dict()


@app.get("/api/logs")
async def query_logs(
    service: str | None = None,
    level: str | None = None,
    limit: int = 100,
    authorization: str | None = Header(None),
) -> list[dict[str, Any]]:
    verify_bearer(authorization)
    results = _logs
    if service:
        results = [entry for entry in results if entry.service == service]
    if level:
        results = [entry for entry in results if entry.level == level.upper()]
    return [entry.to_dict() for entry in results[-limit:]]
