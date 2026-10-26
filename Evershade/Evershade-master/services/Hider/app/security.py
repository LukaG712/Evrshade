"""Hider — Security management module.

Provides:
- Agent tool permissions management
- Service-to-service auth enforcement
- SSRF protection audit
- Secure configuration handling
- Auditable sensitive actions
- Permission policies and role-based access
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from evershade_db import Database

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manage security policies, permissions, and audit trails."""

    def __init__(self, db: Database, http_client: Any):
        self.db = db
        self.http_client = http_client

    # ─── Agent Tool Permissions ──────────────────────────────────────────

    async def get_agent_permissions(
        self, agent_id: str
    ) -> Dict[str, Any]:
        """Get all permissions for an agent."""
        row = await self.db.fetchone(
            "SELECT * FROM agent_permissions WHERE agent_id = ?",
            (agent_id,),
        )
        if not row:
            return {
                "agent_id": agent_id,
                "permissions": {},
                "allowed_tools": [],
                "denied_tools": [],
                "allowed_services": [],
                "denied_services": [],
                "max_execution_time": 300,
                "max_file_size_mb": 10,
                "network_access": "internal",
            }

        return {
            **row,
            "permissions": json.loads(row.get("permissions", "{}")),
            "allowed_tools": json.loads(row.get("allowed_tools", "[]")),
            "denied_tools": json.loads(row.get("denied_tools", "[]")),
            "allowed_services": json.loads(row.get("allowed_services", "[]")),
            "denied_services": json.loads(row.get("denied_services", "[]")),
        }

    async def set_agent_permissions(
        self,
        agent_id: str,
        permissions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Set permissions for an agent."""
        allowed_tools = permissions.get("allowed_tools", [])
        denied_tools = permissions.get("denied_tools", [])
        allowed_services = permissions.get("allowed_services", [])
        denied_services = permissions.get("denied_services", [])
        max_execution_time = permissions.get("max_execution_time", 300)
        max_file_size_mb = permissions.get("max_file_size_mb", 10)
        network_access = permissions.get("network_access", "internal")

        existing = await self.db.fetchone(
            "SELECT id FROM agent_permissions WHERE agent_id = ?",
            (agent_id,),
        )

        if existing:
            await self.db.execute(
                """UPDATE agent_permissions
                   SET permissions = ?, allowed_tools = ?, denied_tools = ?,
                       allowed_services = ?, denied_services = ?,
                       max_execution_time = ?, max_file_size_mb = ?,
                       network_access = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
                   WHERE agent_id = ?""",
                (
                    json.dumps(permissions),
                    json.dumps(allowed_tools),
                    json.dumps(denied_tools),
                    json.dumps(allowed_services),
                    json.dumps(denied_services),
                    max_execution_time,
                    max_file_size_mb,
                    network_access,
                    agent_id,
                ),
            )
        else:
            await self.db.execute(
                """INSERT INTO agent_permissions
                   (id, agent_id, permissions, allowed_tools, denied_tools,
                    allowed_services, denied_services, max_execution_time,
                    max_file_size_mb, network_access)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    agent_id,
                    json.dumps(permissions),
                    json.dumps(allowed_tools),
                    json.dumps(denied_tools),
                    json.dumps(allowed_services),
                    json.dumps(denied_services),
                    max_execution_time,
                    max_file_size_mb,
                    network_access,
                ),
            )

        # Audit log
        await self._audit_action(
            agent_id=agent_id,
            action="set_permissions",
            details=f"Updated permissions for agent {agent_id}",
            actor=permissions.get("actor", "system"),
        )

        return await self.get_agent_permissions(agent_id)

    async def check_tool_permission(
        self,
        agent_id: str,
        tool_name: str,
    ) -> bool:
        """Check if an agent is allowed to use a specific tool."""
        perms = await self.get_agent_permissions(agent_id)

        # If allowed_tools is set, tool must be in the list
        if perms.get("allowed_tools"):
            if tool_name not in perms["allowed_tools"]:
                return False

        # If denied_tools is set, tool must not be in the list
        if perms.get("denied_tools"):
            if tool_name in perms["denied_tools"]:
                return False

        return True

    async def check_service_permission(
        self,
        agent_id: str,
        service_name: str,
    ) -> bool:
        """Check if an agent is allowed to call a specific service."""
        perms = await self.get_agent_permissions(agent_id)

        # If allowed_services is set, service must be in the list
        if perms.get("allowed_services"):
            if service_name not in perms["allowed_services"]:
                return False

        # If denied_services is set, service must not be in the list
        if perms.get("denied_services"):
            if service_name in perms["denied_services"]:
                return False

        return True

    # ─── Service-to-Service Auth ─────────────────────────────────────────

    async def get_service_token(
        self, service_name: str
    ) -> Optional[str]:
        """Get the JWT token for a service."""
        row = await self.db.fetchone(
            "SELECT * FROM service_tokens WHERE service_name = ? AND active = 1",
            (service_name,),
        )
        if not row:
            return None
        return row.get("token")

    async def rotate_service_token(
        self, service_name: str, actor: str = "admin"
    ) -> Dict[str, Any]:
        """Rotate a service's JWT token."""
        import jwt

        existing = await self.db.fetchone(
            "SELECT id FROM service_tokens WHERE service_name = ?",
            (service_name,),
        )

        # Generate new token
        token = jwt.encode(
            {
                "sub": service_name,
                "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc).replace(year=datetime.now().year + 1),
            },
            "evershade-internal-secret",
            algorithm="HS256",
        )

        if existing:
            await self.db.execute(
                """UPDATE service_tokens
                   SET token = ?, rotated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
                   WHERE service_name = ?""",
                (token, service_name),
            )
        else:
            await self.db.execute(
                """INSERT INTO service_tokens
                   (id, service_name, token)
                   VALUES (?, ?, ?)""",
                (str(uuid.uuid4()), service_name, token),
            )

        await self._audit_action(
            action="rotate_service_token",
            details=f"Rotated token for service {service_name}",
            actor=actor,
        )

        return {"service_name": service_name, "token": token}

    # ─── Security Audit ──────────────────────────────────────────────────

    async def _audit_action(
        self,
        action: str,
        details: str = "",
        actor: str = "system",
        agent_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """Log a security-relevant action."""
        await self.db.execute(
            """INSERT INTO security_audit
               (id, action, details, actor, agent_id, ip_address, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()),
                action,
                details,
                actor,
                agent_id,
                ip_address or "",
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    async def get_security_audit(
        self,
        action: Optional[str] = None,
        actor: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query security audit log."""
        query = "SELECT * FROM security_audit WHERE 1=1"
        params: List[Any] = []

        if action:
            query += " AND action = ?"
            params.append(action)
        if actor:
            query += " AND actor = ?"
            params.append(actor)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        return await self.db.fetchall(query, params)

    # ─── SSRF Protection Audit ───────────────────────────────────────────

    async def log_ssrf_check(
        self,
        url: str,
        blocked: bool,
        reason: str = "",
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Log an SSRF protection check."""
        await self.db.execute(
            """INSERT INTO ssrf_audit
               (id, url, blocked, reason, agent_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()),
                url,
                1 if blocked else 0,
                reason,
                agent_id or "",
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        if blocked:
            await self._audit_action(
                action="ssrf_blocked",
                details=f"Blocked URL: {url} ({reason})",
                agent_id=agent_id,
            )

        return {
            "url": url,
            "blocked": blocked,
            "reason": reason,
        }

    async def get_ssrf_audit(
        self,
        blocked_only: bool = True,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get SSRF protection audit log."""
        query = "SELECT * FROM ssrf_audit WHERE 1=1"
        params: List[Any] = []

        if blocked_only:
            query += " AND blocked = 1"

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        rows = await self.db.fetchall(query, params)
        return [{**row, "blocked": bool(row["blocked"])} for row in rows]

    # ─── Security Summary ────────────────────────────────────────────────

    async def get_security_summary(self) -> Dict[str, Any]:
        """Get a summary of security status."""
        # Count agents with permissions
        agents_with_perms = await self.db.fetchone(
            "SELECT COUNT(*) as cnt FROM agent_permissions"
        )

        # Count active service tokens
        active_tokens = await self.db.fetchone(
            "SELECT COUNT(*) as cnt FROM service_tokens WHERE active = 1"
        )

        # Recent security events
        recent_events = await self.db.fetchall(
            """SELECT action, COUNT(*) as cnt
            FROM security_audit
            WHERE created_at >= datetime('now', '-24 hours')
            GROUP BY action
            ORDER BY cnt DESC"""
        )

        # SSRF blocks in last 24 hours
        ssrf_blocks = await self.db.fetchone(
            """SELECT COUNT(*) as cnt
            FROM ssrf_audit
            WHERE blocked = 1
            AND created_at >= datetime('now', '-24 hours')"""
        )

        # Secret access audit
        secret_access = await self.db.fetchall(
            """SELECT action, COUNT(*) as cnt
            FROM audit_log
            WHERE created_at >= datetime('now', '-24 hours')
            GROUP BY action
            ORDER BY cnt DESC"""
        )

        return {
            "agents_with_permissions": agents_with_perms["cnt"] if agents_with_perms else 0,
            "active_service_tokens": active_tokens["cnt"] if active_tokens else 0,
            "recent_security_events": recent_events,
            "ssrf_blocks_24h": ssrf_blocks["cnt"] if ssrf_blocks else 0,
            "secret_access_24h": secret_access,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ─── Content Safety ──────────────────────────────────────────────────

    async def log_content_check(
        self,
        content_type: str,
        source: str,
        blocked: bool,
        reason: str = "",
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Log a content safety check for untrusted content."""
        await self.db.execute(
            """INSERT INTO content_safety_audit
               (id, content_type, source, blocked, reason, agent_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()),
                content_type,
                source,
                1 if blocked else 0,
                reason,
                agent_id or "",
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        if blocked:
            await self._audit_action(
                action="content_blocked",
                details=f"Blocked {content_type} from {source}: {reason}",
                agent_id=agent_id,
            )

        return {
            "content_type": content_type,
            "source": source,
            "blocked": blocked,
            "reason": reason,
        }
