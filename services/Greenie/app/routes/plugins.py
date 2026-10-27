"""Greenie — Plugin management routes.

Provides CRUD for plugins (tools, resources, prompts, integrations)
and MCP server management.
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, HTTPException

from app.database import db

router = APIRouter()


@router.get("/")
async def list_plugins():
    """List all installed plugins."""
    rows = await db.fetchall("SELECT * FROM plugins ORDER BY installed_at DESC")
    plugins = []
    for row in rows:
        d = dict(row)
        d["enabled"] = bool(d.get("enabled", 1))
        d["config"] = json.loads(d.get("config", "{}"))
        plugins.append(d)
    return {"plugins": plugins}


@router.post("/")
async def install_plugin(data: dict):
    """Install a new plugin."""
    name = data.get("name", "").strip()
    source = data.get("source", "").strip()
    plugin_type = data.get("type", "tool")
    description = data.get("description", "")
    if not name:
        raise HTTPException(status_code=400, detail="Plugin name is required")
    if not source:
        raise HTTPException(status_code=400, detail="Plugin source is required")
    plugin_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO plugins (id, name, description, type, source) VALUES (?, ?, ?, ?, ?)",
        (plugin_id, name, description, plugin_type, source),
    )
    return {"id": plugin_id, "name": name, "source": source, "type": plugin_type}


@router.patch("/{plugin_id}")
async def update_plugin(plugin_id: str, data: dict):
    """Update a plugin (enable/disable/config)."""
    existing = await db.fetchone("SELECT * FROM plugins WHERE id = ?", (plugin_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Plugin not found")
    if "enabled" in data:
        await db.execute(
            "UPDATE plugins SET enabled = ? WHERE id = ?",
            (int(data["enabled"]), plugin_id),
        )
    if "config" in data:
        await db.execute(
            "UPDATE plugins SET config = ? WHERE id = ?",
            (json.dumps(data["config"]), plugin_id),
        )
    return {"id": plugin_id, "updated": True}


@router.delete("/{plugin_id}")
async def uninstall_plugin(plugin_id: str):
    """Uninstall a plugin."""
    existing = await db.fetchone("SELECT * FROM plugins WHERE id = ?", (plugin_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Plugin not found")
    await db.execute("DELETE FROM plugins WHERE id = ?", (plugin_id,))
    return {"id": plugin_id, "deleted": True}
