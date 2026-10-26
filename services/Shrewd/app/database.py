"""Shrewd — SQLite database layer.

Uses the shared evershade-db package for async SQLite access with WAL mode.

Usage:

    from app.database import db, init_db
    rows = await db.fetchall("SELECT * FROM models")
"""

from __future__ import annotations

import os

from evershade_db import Database, ensure_db_path

DB_PATH = os.getenv("SHREWD_DB_PATH", "/data/shrewd.db")

# Shared database instance
db = Database(ensure_db_path(DB_PATH))


async def init_db() -> None:
    """Initialize the database and create all tables."""
    await db.create_tables_from_sql(_SCHEMA_SQL)


async def get_db_instance() -> Database:
    """Get the shared database instance (for backward compatibility with routes)."""
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS providers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    base_url TEXT NOT NULL DEFAULT '',
    api_key TEXT DEFAULT '',
    enabled INTEGER DEFAULT 1,
    config TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    provider_id TEXT NOT NULL,
    context_window INTEGER DEFAULT 8192,
    max_tokens INTEGER DEFAULT 4096,
    supports_vision INTEGER DEFAULT 0,
    supports_tools INTEGER DEFAULT 0,
    supports_embeddings INTEGER DEFAULT 0,
    input_cost_per_token REAL DEFAULT 0.0,
    output_cost_per_token REAL DEFAULT 0.0,
    enabled INTEGER DEFAULT 1,
    config TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (provider_id) REFERENCES providers(id)
);

CREATE TABLE IF NOT EXISTS usage (
    id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    estimated_cost REAL DEFAULT 0.0,
    duration_ms INTEGER DEFAULT 0,
    status TEXT DEFAULT 'success' CHECK(status IN ('success', 'error', 'timeout')),
    error_message TEXT DEFAULT '',
    user_id TEXT DEFAULT '',
    request_id TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (model_id) REFERENCES models(id),
    FOREIGN KEY (provider_id) REFERENCES providers(id)
);

CREATE TABLE IF NOT EXISTS routing_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    task_type TEXT DEFAULT '',
    min_capability TEXT DEFAULT '',
    max_cost REAL DEFAULT 0.0,
    model_name TEXT DEFAULT '',
    fallback_models TEXT DEFAULT '[]',
    max_retries INTEGER DEFAULT 2,
    timeout_seconds REAL DEFAULT 120.0,
    enabled INTEGER DEFAULT 1,
    priority INTEGER NOT NULL DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS privacy_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    level TEXT NOT NULL DEFAULT 'standard' CHECK(level IN ('public', 'standard', 'confidential', 'restricted')),
    allowed_providers TEXT DEFAULT '[]',
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_models_provider_id ON models(provider_id);
CREATE INDEX IF NOT EXISTS idx_usage_model_id ON usage(model_id);
CREATE INDEX IF NOT EXISTS idx_usage_created ON usage(created_at);
CREATE INDEX IF NOT EXISTS idx_routing_rules_priority ON routing_rules(priority);
"""
