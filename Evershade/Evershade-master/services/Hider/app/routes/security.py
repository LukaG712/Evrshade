"""Hider — Security management routes.

Endpoints for agent permissions, service tokens, security audit,
SSRF protection audit, and content safety.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request

from evershade.errors import EvershadeError

from app.security import SecurityManager

router = APIRouter(prefix="/api/security", tags=["security"])


# ─── Agent Permissions ──────────────────────────────────────────────────────

@router.get("/permissions/{agent_id}")
async def get_agent_permissions(agent_id: str, request: Request) -> Dict[str, Any]:
    """Get permissions for an agent."""
    manager: SecurityManager = request.app.state.security_manager
    return await manager.get_agent_permissions(agent_id)


@router.put("/permissions/{agent_id}")
async def set_agent_permissions(
    agent_id: str,
    request: Request,
) -> Dict[str, Any]:
    """Set permissions for an agent."""
    manager: SecurityManager = request.app.state.security_manager
    permissions = await request.json()
    permissions["actor"] = request.headers.get("X-Actor", "api")
    return await manager.set_agent_permissions(agent_id, permissions)


@router.post("/permissions/{agent_id}/check-tool")
async def check_tool_permission(
    agent_id: str,
    tool_name: str,
    request: Request,
) -> Dict[str, Any]:
    """Check if an agent can use a specific tool."""
    manager: SecurityManager = request.app.state.security_manager
    allowed = await manager.check_tool_permission(agent_id, tool_name)
    return {"agent_id": agent_id, "tool": tool_name, "allowed": allowed}


@router.post("/permissions/{agent_id}/check-service")
async def check_service_permission(
    agent_id: str,
    service_name: str,
    request: Request,
) -> Dict[str, Any]:
    """Check if an agent can call a specific service."""
    manager: SecurityManager = request.app.state.security_manager
    allowed = await manager.check_service_permission(agent_id, service_name)
    return {"agent_id": agent_id, "service": service_name, "allowed": allowed}


# ─── Service Tokens ─────────────────────────────────────────────────────────

@router.post("/tokens/{service_name}/rotate")
async def rotate_service_token(
    service_name: str,
    request: Request,
) -> Dict[str, Any]:
    """Rotate a service's JWT token."""
    manager: SecurityManager = request.app.state.security_manager
    actor = request.headers.get("X-Actor", "admin")
    return await manager.rotate_service_token(service_name, actor)


# ─── Security Audit ─────────────────────────────────────────────────────────

@router.get("/audit")
async def get_security_audit(
    request: Request,
    action: Optional[str] = None,
    actor: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Query security audit log."""
    manager: SecurityManager = request.app.state.security_manager
    return await manager.get_security_audit(action, actor, limit)


@router.get("/summary")
async def get_security_summary(request: Request) -> Dict[str, Any]:
    """Get security status summary."""
    manager: SecurityManager = request.app.state.security_manager
    return await manager.get_security_summary()


# ─── SSRF Audit ─────────────────────────────────────────────────────────────

@router.post("/ssrf/log")
async def log_ssrf_check(request: Request) -> Dict[str, Any]:
    """Log an SSRF protection check."""
    manager: SecurityManager = request.app.state.security_manager
    body = await request.json()
    return await manager.log_ssrf_check(
        url=body.get("url", ""),
        blocked=body.get("blocked", False),
        reason=body.get("reason", ""),
        agent_id=body.get("agent_id"),
    )


@router.get("/ssrf/audit")
async def get_ssrf_audit(
    request: Request,
    blocked_only: bool = True,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Get SSRF protection audit log."""
    manager: SecurityManager = request.app.state.security_manager
    return await manager.get_ssrf_audit(blocked_only, limit)


# ─── Content Safety ─────────────────────────────────────────────────────────

@router.post("/content/log")
async def log_content_check(request: Request) -> Dict[str, Any]:
    """Log a content safety check."""
    manager: SecurityManager = request.app.state.security_manager
    body = await request.json()
    return await manager.log_content_check(
        content_type=body.get("content_type", ""),
        source=body.get("source", ""),
        blocked=body.get("blocked", False),
        reason=body.get("reason", ""),
        agent_id=body.get("agent_id"),
    )
