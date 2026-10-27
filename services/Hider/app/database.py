"""Hider — SQLite database layer.

Provides async SQLite access for encrypted secrets, versioned config, and audit logs.
"""

from __future__ import annotations

import os

from evershade_db import Database, ensure_db_path

DB_PATH = os.getenv("DB_PATH", "/app/data/hider.db")

# Shared database instance
db = Database(ensure_db_path(DB_PATH))


async def init_db() -> None:
    """Initialize the database and create all tables."""
    await db.create_tables_from_sql(_SCHEMA_SQL)


async def get_db_instance() -> Database:
    """Get the shared database instance."""
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS secrets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    encrypted_value TEXT NOT NULL,
    iv TEXT NOT NULL,
    tag TEXT NOT NULL,
    description TEXT DEFAULT '',
    version INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS secret_history (
    id TEXT PRIMARY KEY,
    secret_id TEXT NOT NULL,
    encrypted_value TEXT NOT NULL,
    iv TEXT NOT NULL,
    tag TEXT NOT NULL,
    version INTEGER NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('created', 'updated', 'deleted')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (secret_id) REFERENCES secrets(id)
);

CREATE TABLE IF NOT EXISTS config_entries (
    id TEXT PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    is_encrypted INTEGER DEFAULT 0,
    description TEXT DEFAULT '',
    version INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    details TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_secret_history_secret_id ON secret_history(secret_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_resource_id ON audit_log(resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);

"""
