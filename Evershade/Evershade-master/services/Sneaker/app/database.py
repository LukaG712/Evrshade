"""Sneaker — SQLite database layer.

Uses the shared evershade-db package for async SQLite access with WAL mode.

Usage:

    from app.database import db, init_db
    rows = await db.fetchall("SELECT * FROM traces")
"""

from __future__ import annotations

import os
from evershade_db import Database, ensure_db_path

DB_PATH = os.getenv("SNEAKER_DB_PATH", "/data/sneaker.db")

# Shared database instance
db = Database(ensure_db_path(DB_PATH))


async def init_db() -> None:
    """Initialize the database and create all tables."""
    await db.create_tables_from_sql(_SCHEMA_SQL)


async def get_db_instance() -> Database:
    """Get the shared database instance (for backward compatibility with routes)."""
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS traces (
    id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    span_id TEXT NOT NULL,
    parent_span_id TEXT DEFAULT '',
    service_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    kind TEXT DEFAULT 'SPAN_KIND_UNSPECIFIED',
    status TEXT DEFAULT 'UNSET' CHECK(status IN ('UNSET', 'OK', 'ERROR')),
    start_time INTEGER NOT NULL,
    end_time INTEGER NOT NULL,
    duration_us INTEGER DEFAULT 0,
    tags TEXT DEFAULT '{}',
    events TEXT DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS logs (
    id TEXT PRIMARY KEY,
    trace_id TEXT DEFAULT '',
    span_id TEXT DEFAULT '',
    service_name TEXT NOT NULL,
    level TEXT NOT NULL DEFAULT 'info' CHECK(level IN ('debug', 'info', 'warn', 'error', 'critical')),
    message TEXT NOT NULL,
    body TEXT DEFAULT '',
    attributes TEXT DEFAULT '{}',
    timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS metrics (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    service_name TEXT NOT NULL,
    metric_type TEXT NOT NULL CHECK(metric_type IN ('counter', 'gauge', 'histogram')),
    value REAL NOT NULL,
    labels TEXT DEFAULT '{}',
    timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS alert_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    metric_name TEXT NOT NULL,
    condition TEXT NOT NULL CHECK(condition IN ('gt', 'lt', 'gte', 'lte', 'eq')),
    threshold REAL NOT NULL,
    window_seconds INTEGER DEFAULT 300,
    severity TEXT DEFAULT 'warning' CHECK(severity IN ('info', 'warning', 'critical')),
    enabled INTEGER DEFAULT 1,
    last_triggered TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS alert_history (
    id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    threshold REAL NOT NULL,
    severity TEXT NOT NULL,
    message TEXT DEFAULT '',
    triggered_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_traces_trace_id ON traces(trace_id);
CREATE INDEX IF NOT EXISTS idx_traces_service ON traces(service_name);
CREATE INDEX IF NOT EXISTS idx_traces_created ON traces(created_at);
CREATE INDEX IF NOT EXISTS idx_logs_service ON logs(service_name);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name);
CREATE INDEX IF NOT EXISTS idx_metrics_service ON metrics(service_name);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_alert_history_rule ON alert_history(rule_id);
CREATE INDEX IF NOT EXISTS idx_alert_history_triggered ON alert_history(triggered_at);
"""
