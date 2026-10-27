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


# --- MCP Server Management ---


@router.get("/mcp/servers")
async def list_mcp_servers():
    """List all configured MCP servers."""
    rows = await db.fetchall("SELECT * FROM mcp_servers ORDER BY created_at DESC")
    servers = []
    for row in rows:
        d = dict(row)
        d["connected"] = bool(d.get("connected", 0))
        d["config"] = json.loads(d.get("config", "{}"))
        d["tools"] = json.loads(d.get("tools", "[]"))
        servers.append(d)
    return {"servers": servers}


@router.post("/mcp/servers")
async def add_mcp_server(data: dict):
    """Add a new MCP server."""
    name = data.get("name", "").strip()
    url = data.get("url", "").strip()
    if not name or not url:
        raise HTTPException(status_code=400, detail="Name and URL are required")
    existing = await db.fetchone("SELECT * FROM mcp_servers WHERE name = ?", (name,))
    if existing:
        raise HTTPException(
            status_code=409, detail="MCP server with this name already exists"
        )
    server_id = str(uuid.uuid4())
    transport = "stdio"
    if url.startswith(("http://", "https://")):
        transport = "http"
    elif url.startswith("sse://"):
        transport = "sse"
    await db.execute(
        "INSERT INTO mcp_servers (id, name, url, transport) VALUES (?, ?, ?, ?)",
        (server_id, name, url, transport),
    )
    return {"id": server_id, "name": name, "url": url, "transport": transport}


@router.delete("/mcp/servers/{server_name}")
async def remove_mcp_server(server_name: str):
    """Remove an MCP server."""
    existing = await db.fetchone(
        "SELECT * FROM mcp_servers WHERE name = ?", (server_name,)
    )
    if not existing:
        raise HTTPException(status_code=404, detail="MCP server not found")
    await db.execute("DELETE FROM mcp_servers WHERE name = ?", (server_name,))
    return {"name": server_name, "deleted": True}
