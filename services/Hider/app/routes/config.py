"""Hider — Configuration management routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.database import db
from app.models import ConfigCreate, ConfigResponse, gen_id

router = APIRouter()


@router.post("/", status_code=201)
async def create_config(cfg: ConfigCreate) -> ConfigResponse:
    """Create a new configuration entry."""
    cid = gen_id()
    await db.execute(
        "INSERT INTO config_entries (id, key, value, is_encrypted, description) VALUES (?, ?, ?, ?, ?)",
        (cid, cfg.key, cfg.value, int(cfg.is_encrypted), cfg.description),
    )
    row = await db.fetchone("SELECT * FROM config_entries WHERE id = ?", (cid,))
    return ConfigResponse(**row)


@router.get("/")
async def list_config() -> list[ConfigResponse]:
    """List all configuration entries."""
    rows = await db.fetchall("SELECT * FROM config_entries ORDER BY key")
    return [ConfigResponse(**r) for r in rows]


@router.get("/{config_key}")
async def get_config(config_key: str) -> ConfigResponse:
    """Get a configuration entry by key."""
    row = await db.fetchone("SELECT * FROM config_entries WHERE key = ?", (config_key,))
    if not row:
        raise HTTPException(status_code=404, detail="Config key not found")
    return ConfigResponse(**row)


@router.put("/{config_key}")
async def update_config(config_key: str, value: str) -> ConfigResponse:
    """Update a configuration entry's value."""
    row = await db.fetchone("SELECT * FROM config_entries WHERE key = ?", (config_key,))
    if not row:
        raise HTTPException(status_code=404, detail="Config key not found")
    new_version = row["version"] + 1
    await db.execute(
        "UPDATE config_entries SET value = ?, version = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE key = ?",
        (value, new_version, config_key),
    )
    row = await db.fetchone("SELECT * FROM config_entries WHERE key = ?", (config_key,))
    return ConfigResponse(**row)


@router.delete("/{config_key}", status_code=204)
async def delete_config(config_key: str) -> None:
    """Delete a configuration entry."""
    cursor = await db.execute("DELETE FROM config_entries WHERE key = ?", (config_key,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Config key not found")
