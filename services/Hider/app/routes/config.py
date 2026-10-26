"""Hider — Configuration management routes.

Versioned configuration entries with history tracking.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter

from evershade.errors import EvershadeError

from app.database import db
from app.models import (
    ConfigCreate,
    ConfigHistoryResponse,
    ConfigResponse,
    ConfigUpdate,
)

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("", response_model=list[ConfigResponse])
async def list_config():
    """List all configuration entries (latest version only)."""
    rows = await db.fetchall(
        """SELECT ce.* FROM config_entries ce
           INNER JOIN (SELECT key, MAX(version) as max_ver FROM config_entries GROUP BY key) latest
           ON ce.key = latest.key AND ce.version = latest.max_ver
           ORDER BY ce.key"""
    )
    return [ConfigResponse(**row) for row in rows]


@router.get("/{config_key}", response_model=ConfigResponse)
async def get_config(config_key: str):
    """Get the latest value for a configuration key."""
    row = await db.fetchone(
        "SELECT * FROM config_entries WHERE key = ? ORDER BY version DESC LIMIT 1",
        (config_key,),
    )
    if not row:
        raise EvershadeError.not_found(f"Config {config_key} not found")
    return ConfigResponse(**row)


@router.get("/{config_key}/history", response_model=list[ConfigHistoryResponse])
async def get_config_history(config_key: str, limit: int = 50):
    """Get version history for a configuration key."""
    rows = await db.fetchall(
        "SELECT * FROM config_history WHERE key = ? ORDER BY version DESC LIMIT ?",
        (config_key, limit),
    )
    return [ConfigHistoryResponse(**row) for row in rows]


@router.post("", response_model=ConfigResponse, status_code=201)
async def create_config(config: ConfigCreate):
    """Create a new configuration entry."""
    # Check if key already exists
    existing = await db.fetchone(
        "SELECT * FROM config_entries WHERE key = ? ORDER BY version DESC LIMIT 1",
        (config.key,),
    )
    if existing:
        raise EvershadeError.conflict(f"Config {config.key} already exists, use PUT to update")

    config_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO config_entries (id, key, value, version, description)
           VALUES (?, ?, ?, 1, ?)""",
        (config_id, config.key, config.value, config.description),
    )
    # Add to history
    history_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO config_history (id, key, value, version, changed_by)
           VALUES (?, ?, ?, 1, 'api')""",
        (history_id, config.key, config.value),
    )

    row = await db.fetchone("SELECT * FROM config_entries WHERE id = ?", (config_id,))
    return ConfigResponse(**row)


@router.put("/{config_key}", response_model=ConfigResponse)
async def update_config(config_key: str, config: ConfigUpdate):
    """Update a configuration entry (creates a new version)."""
    # Get current version
    current = await db.fetchone(
        "SELECT * FROM config_entries WHERE key = ? ORDER BY version DESC LIMIT 1",
        (config_key,),
    )
    if not current:
        raise EvershadeError.not_found(f"Config {config_key} not found")

    new_version = current["version"] + 1
    config_id = str(uuid.uuid4())

    # Insert new version
    desc = config.description if config.description is not None else current["description"]
    await db.execute(
        """INSERT INTO config_entries (id, key, value, version, description)
           VALUES (?, ?, ?, ?, ?)""",
        (config_id, config_key, config.value, new_version, desc),
    )
    # Add to history
    history_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO config_history (id, key, value, version, changed_by)
           VALUES (?, ?, ?, ?, 'api')""",
        (history_id, config_key, config.value, new_version),
    )

    row = await db.fetchone("SELECT * FROM config_entries WHERE id = ?", (config_id,))
    return ConfigResponse(**row)


@router.delete("/{config_key}", status_code=204)
async def delete_config(config_key: str):
    """Delete a configuration entry and its history."""
    existing = await db.fetchone("SELECT * FROM config_entries WHERE key = ?", (config_key,))
    if not existing:
        raise EvershadeError.not_found(f"Config {config_key} not found")
    await db.execute("DELETE FROM config_entries WHERE key = ?", (config_key,))
    await db.execute("DELETE FROM config_history WHERE key = ?", (config_key,))


@router.get("/all", response_model=dict[str, str])
async def get_all_config():
    """Get all configuration as a flat key-value map (latest versions)."""
    rows = await db.fetchall(
        """SELECT ce.key, ce.value FROM config_entries ce
           INNER JOIN (SELECT key, MAX(version) as max_ver FROM config_entries GROUP BY key) latest
           ON ce.key = latest.key AND ce.version = latest.max_ver"""
    )
    return {row["key"]: row["value"] for row in rows}
