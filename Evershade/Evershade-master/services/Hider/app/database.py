"""Hider — SQLite database layer.

Uses the shared evershade-db package for async SQLite access with WAL mode.

Usage:

    from app.database import db, init_db
    rows = await db.fetchall("SELECT * FROM secrets")
"""

from __future__ import annotations

import os
from evershade_db import Database, ensure_db_path

DB_PATH = os.getenv("HIDER_DB_PATH", "/data/hider.db")

# Shared database instance
db = Database(ensure_db_path(DB_PATH))


async def init_db() -> None:
    """Initialize the database and create all tables."""
    await db.create_tables_from_sql(_SCHEMA_SQL)


async def get_db_instance() -> Database:
    """Get the shared database instance (for backward compatibility with routes)."""
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS secrets (
    id TEXT PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    encrypted_value BLOB NOT NULL,
    iv BLOB NOT NULL,
    tag BLOB NOT NULL,
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS config_entries (
    id TEXT PRIMARY KEY,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS config_history (
    id TEXT PRIMARY KEY,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    version INTEGER NOT NULL,
    changed_by TEXT DEFAULT '',
    changed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,
    secret_key TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('create', 'read', 'update', 'delete')),
    actor TEXT DEFAULT '',
    ip_address TEXT DEFAULT '',
    success INTEGER DEFAULT 1,
    details TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_secrets_key ON secrets(key);
CREATE INDEX IF NOT EXISTS idx_config_key ON config_entries(key);
CREATE INDEX IF NOT EXISTS idx_config_history_key ON config_history(key);
CREATE INDEX IF NOT EXISTS idx_audit_secret ON audit_log(secret_key);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);

-- Security Management Tables

CREATE TABLE IF NOT EXISTS agent_permissions (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL UNIQUE,
    permissions TEXT DEFAULT '{}',
    allowed_tools TEXT DEFAULT '[]',
    denied_tools TEXT DEFAULT '[]',
    allowed_services TEXT DEFAULT '[]',
    denied_services TEXT DEFAULT '[]',
    max_execution_time INTEGER DEFAULT 300,
    max_file_size_mb INTEGER DEFAULT 10,
    network_access TEXT DEFAULT 'internal' CHECK(network_access IN ('internal', 'restricted', 'full')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS service_tokens (
    id TEXT PRIMARY KEY,
    service_name TEXT NOT NULL UNIQUE,
    token TEXT NOT NULL,
    active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    rotated_at TEXT
);

CREATE TABLE IF NOT EXISTS security_audit (
    id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    details TEXT DEFAULT '',
    actor TEXT DEFAULT 'system',
    agent_id TEXT DEFAULT '',
    ip_address TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS ssrf_audit (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    blocked INTEGER DEFAULT 0,
    reason TEXT DEFAULT '',
    agent_id TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS content_safety_audit (
    id TEXT PRIMARY KEY,
    content_type TEXT NOT NULL,
    source TEXT NOT NULL,
    blocked INTEGER DEFAULT 0,
    reason TEXT DEFAULT '',
    agent_id TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_agent_perms_agent ON agent_permissions(agent_id);
CREATE INDEX IF NOT EXISTS idx_service_tokens_name ON service_tokens(service_name);
CREATE INDEX IF NOT EXISTS idx_security_audit_action ON security_audit(action);
CREATE INDEX IF NOT EXISTS idx_security_audit_created ON security_audit(created_at);
CREATE INDEX IF NOT EXISTS idx_ssrf_audit_created ON ssrf_audit(created_at);
CREATE INDEX IF NOT EXISTS idx_content_safety_created ON content_safety_audit(created_at);
"""
