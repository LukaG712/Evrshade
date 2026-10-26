"""Tests for evershade_db — Database utilities."""

import os
import tempfile
import pytest

from evershade_db import Database, ensure_db_path, init_wal_mode


class TestEnsureDbPath:
    """Test ensure_db_path utility."""

    def test_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "subdir", "test.db")
            result = ensure_db_path(db_path)
            assert os.path.isdir(os.path.join(tmp, "subdir"))
            assert result.endswith("test.db")

    def test_returns_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "test.db")
            result = ensure_db_path(db_path)
            assert os.path.isabs(result)


class TestDatabase:
    """Test Database class."""

    @pytest.mark.asyncio
    async def test_connect_and_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Database(os.path.join(tmp, "test.db"))
            conn = await db.connect()
            assert conn is not None
            await db.close()

    @pytest.mark.asyncio
    async def test_execute(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Database(os.path.join(tmp, "test.db"))
            await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            await db.execute("INSERT INTO test (name) VALUES (?)", ("hello",))
            result = await db.fetchone("SELECT * FROM test")
            assert result["name"] == "hello"
            await db.close()

    @pytest.mark.asyncio
    async def test_fetchall(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Database(os.path.join(tmp, "test.db"))
            await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            await db.execute("INSERT INTO test (name) VALUES (?)", ("a",))
            await db.execute("INSERT INTO test (name) VALUES (?)", ("b",))
            rows = await db.fetchall("SELECT * FROM test")
            assert len(rows) == 2
            await db.close()

    @pytest.mark.asyncio
    async def test_transaction_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Database(os.path.join(tmp, "test.db"))
            await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            async with db.transaction() as conn:
                await conn.execute("INSERT INTO test (name) VALUES (?)", ("tx",))
            result = await db.fetchone("SELECT * FROM test")
            assert result["name"] == "tx"
            await db.close()

    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Database(os.path.join(tmp, "test.db"))
            await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            try:
                async with db.transaction() as conn:
                    await conn.execute("INSERT INTO test (name) VALUES (?)", ("tx",))
                    raise ValueError("fail")
            except ValueError:
                pass
            result = await db.fetchone("SELECT * FROM test")
            assert result is None
            await db.close()

    @pytest.mark.asyncio
    async def test_create_tables_from_sql(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Database(os.path.join(tmp, "test.db"))
            await db.create_tables_from_sql("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );
            """)
            result = await db.fetchone("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            assert result is not None
            await db.close()


class TestWalMode:
    """Test WAL mode initialization."""

    def test_sync_wal_mode(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "test.db")
            conn = sqlite3.connect(db_path)
            init_wal_mode(conn)
            mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            assert mode == "wal"
            conn.close()
