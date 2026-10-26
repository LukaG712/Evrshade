"""Poltergeist — SQLite database layer.

Uses the shared evershade-db package for async SQLite access with WAL mode.

Usage:

    from app.database import db, init_db
    rows = await db.fetchall("SELECT * FROM delivery_history")
"""

from __future__ import annotations

import os
from evershade_db import Database, ensure_db_path

DB_PATH = os.getenv("POLTERGEIST_DB_PATH", "/data/poltergeist.db")

# Shared database instance
db = Database(ensure_db_path(DB_PATH))


async def init_db() -> None:
    """Initialize the database and create all tables."""
    await db.create_tables_from_sql(_SCHEMA_SQL)


async def get_db_instance() -> Database:
    """Get the shared database instance (for backward compatibility with routes)."""
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS channels (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK(type IN ('slack', 'discord', 'email', 'telegram')),
    config TEXT NOT NULL DEFAULT '{}',
    enabled INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    channel_type TEXT NOT NULL,
    subject TEXT DEFAULT '',
    body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS pending_queue (
    id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL,
    channel_type TEXT NOT NULL,
    recipient TEXT NOT NULL,
    subject TEXT DEFAULT '',
    body TEXT NOT NULL,
    template_name TEXT DEFAULT '',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    scheduled_at TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS delivery_history (
    id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL,
    channel_type TEXT NOT NULL,
    recipient TEXT NOT NULL,
    subject TEXT DEFAULT '',
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'sent', 'failed', 'retrying')),
    error_message TEXT DEFAULT '',
    retry_count INTEGER DEFAULT 0,
    sent_at TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_pending_scheduled ON pending_queue(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_delivery_status ON delivery_history(status);
CREATE INDEX IF NOT EXISTS idx_delivery_created ON delivery_history(created_at);

-- Notification Rules and Preferences Tables

CREATE TABLE IF NOT EXISTS user_preferences (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    channels TEXT DEFAULT '[]',
    quiet_hours TEXT DEFAULT 'null',
    digest_frequency TEXT DEFAULT 'realtime',
    event_filters TEXT DEFAULT '{}',
    enabled INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS notification_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    conditions TEXT DEFAULT '{}',
    channels TEXT DEFAULT '[]',
    template TEXT DEFAULT '',
    priority INTEGER DEFAULT 5,
    enabled INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS event_notifications (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    source_service TEXT DEFAULT '',
    rule_id TEXT,
    channels TEXT DEFAULT '[]',
    template TEXT DEFAULT '',
    data TEXT DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'sending', 'sent', 'failed')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (rule_id) REFERENCES notification_rules(id)
);

CREATE INDEX IF NOT EXISTS idx_user_prefs_user ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_notif_rules_event ON notification_rules(event_type);
CREATE INDEX IF NOT EXISTS idx_event_notif_status ON event_notifications(status);
CREATE INDEX IF NOT EXISTS idx_event_notif_type ON event_notifications(event_type);
CREATE INDEX IF NOT EXISTS idx_event_notif_created ON event_notifications(created_at);
"""
