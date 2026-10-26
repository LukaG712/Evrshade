"""Slinker — SQLite database layer.

Provides async SQLite access for task execution state, worker registry,
project registration, and session logs.
"""

from __future__ import annotations

import os

from evershade_db import Database, ensure_db_path

DB_PATH = os.getenv("SLINKER_DB_PATH", "/data/slinker.db")

# Shared database instance
db = Database(ensure_db_path(DB_PATH))


async def init_db() -> None:
    """Initialize the database and create all tables."""
    await db.create_tables_from_sql(_SCHEMA_SQL)


async def get_db_instance() -> Database:
    """Get the shared database instance."""
    return db


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    project_id TEXT DEFAULT '',
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    worktree_path TEXT DEFAULT '',
    command TEXT DEFAULT '',
    output TEXT DEFAULT '',
    error TEXT DEFAULT '',
    exit_code INTEGER,
    worker_id TEXT DEFAULT '',
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS workers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'idle' CHECK(status IN ('idle', 'busy', 'stopped')),
    current_task_id TEXT DEFAULT '',
    last_heartbeat TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    repo_url TEXT DEFAULT '',
    branch TEXT DEFAULT 'main',
    worktree_base TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'failed')),
    task_count INTEGER DEFAULT 0,
    started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS session_logs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    task_id TEXT DEFAULT '',
    level TEXT DEFAULT 'info' CHECK(level IN ('debug', 'info', 'warn', 'error')),
    message TEXT NOT NULL DEFAULT '',
    data TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_workers_status ON workers(status);
CREATE INDEX IF NOT EXISTS idx_session_logs_session_id ON session_logs(session_id);

-- Coding Agent Tables

CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    project_id TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'locked', 'deleted')),
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS execution_sessions (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    adapter TEXT NOT NULL,
    workspace_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout')),
    output TEXT,
    error TEXT,
    exit_code INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    completed_at TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

CREATE TABLE IF NOT EXISTS file_changes (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    path TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('created', 'modified', 'deleted')),
    diff TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (session_id) REFERENCES execution_sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_workspaces_project_id ON workspaces(project_id);
CREATE INDEX IF NOT EXISTS idx_execution_sessions_task_id ON execution_sessions(task_id);
CREATE INDEX IF NOT EXISTS idx_execution_sessions_status ON execution_sessions(status);
CREATE INDEX IF NOT EXISTS idx_file_changes_session_id ON file_changes(session_id);

"""
