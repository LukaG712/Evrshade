"""Database conventions and utilities for Evershade services.

Provides SQLite WAL mode setup, connection pooling, and migration helpers.
All Evershade services use SQLite with WAL mode for better concurrency.

Usage:
    from evershade_db import create_engine, init_wal_mode, Base

    engine = create_engine("sqlite:///./app.db")
    init_wal_mode(engine)
"""

from __future__ import annotations

import sqlite3
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiosqlite


def ensure_db_path(db_path: str) -> str:
    """Ensure the directory for the database file exists.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        Absolute path to the database file.
    """
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p.absolute())


def init_wal_mode(conn: sqlite3.Connection) -> None:
    """Enable WAL mode and set optimal SQLite settings.

    Args:
        conn: SQLite connection.
    """
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
    conn.execute("PRAGMA foreign_keys=ON")


async def init_wal_mode_async(conn: aiosqlite.Connection) -> None:
    """Enable WAL mode on an async SQLite connection."""
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA synchronous=NORMAL")
    await conn.execute("PRAGMA cache_size=-64000")
    await conn.execute("PRAGMA foreign_keys=ON")
    await conn.commit()


class Database:
    """Async SQLite database connection manager.

    Usage:
        db = Database("sqlite:///./app.db")
        async with db.connect() as conn:
            await conn.execute("SELECT 1")
    """

    def __init__(self, db_path: str = "./app.db"):
        self.db_path = ensure_db_path(db_path)
        self._pool: aiosqlite.Connection | None = None

    async def connect(self) -> aiosqlite.Connection:
        """Get a database connection with WAL mode enabled."""
        if self._pool is None:
            self._pool = await aiosqlite.connect(self.db_path)
            await init_wal_mode_async(self._pool)
        return self._pool

    async def close(self) -> None:
        """Close the database connection."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Context manager for database transactions."""
        conn = await self.connect()
        try:
            yield conn
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise

    async def execute(self, sql: str, params: tuple | None = None) -> aiosqlite.Cursor:
        """Execute a SQL statement."""
        conn = await self.connect()
        return await conn.execute(sql, params or ())

    async def fetchall(
        self, sql: str, params: tuple | None = None
    ) -> list[dict[str, Any]]:
        """Execute a query and return all rows as dictionaries."""
        conn = await self.connect()
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(sql, params or ())
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def fetchone(
        self, sql: str, params: tuple | None = None
    ) -> dict[str, Any] | None:
        """Execute a query and return a single row as a dictionary."""
        conn = await self.connect()
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(sql, params or ())
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def create_tables_from_sql(self, sql: str) -> None:
        """Execute SQL to create tables."""
        conn = await self.connect()
        await conn.executescript(sql)
        await conn.commit()
