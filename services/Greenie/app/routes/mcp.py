"""Greenie — MCP server management routes.

Provides CRUD for MCP (Model Context Protocol) server configuration.
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, HTTPException

from app.database import db

router = APIRouter()


@router.get("/servers")
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


@router.post("/servers")
async def add_mcp_server(data: dict):
    """Add a new MCP server."""
    name = data.get("name", "").strip()
    url = data.get("url", "").strip()
    if not name or not url:
        raise HTTPException(status_code=400, detail="Name and URL are required")
    existing = await db.fetchone("SELECT * FROM mcp_servers WHERE name = ?", (name,))
    if existing:
        raise HTTPException(status_code=409, detail="MCP server with this name already exists")
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


@router.delete("/servers/{server_name}")
async def remove_mcp_server(server_name: str):
    """Remove an MCP server."""
    existing = await db.fetchone("SELECT * FROM mcp_servers WHERE name = ?", (server_name,))
    if not existing:
        raise HTTPException(status_code=404, detail="MCP server not found")
    await db.execute("DELETE FROM mcp_servers WHERE name = ?", (server_name,))
    return {"name": server_name, "deleted": True}
