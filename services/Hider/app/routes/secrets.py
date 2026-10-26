"""Hider — Secret management routes.

CRUD operations for encrypted secrets with audit logging.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Request

from evershade.errors import EvershadeError

from app.database import db
from app.models import (
    AuditLogResponse,
    SecretCreate,
    SecretResponse,
    SecretUpdate,
)
from app.crypto import encrypt, decrypt

router = APIRouter(prefix="/api/secrets", tags=["secrets"])


async def _audit_log(secret_key: str, action: str, actor: str = "", ip: str = "", success: bool = True, details: str = ""):
    """Record an audit log entry."""
    audit_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO audit_log (id, secret_key, action, actor, ip_address, success, details)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (audit_id, secret_key, action, actor, ip, 1 if success else 0, details),
    )


@router.get("", response_model=list[SecretResponse])
async def list_secrets():
    """List all secret keys (values are not returned for security)."""
    rows = await db.fetchall("SELECT id, key, description, created_at, updated_at FROM secrets ORDER BY key")
    return [SecretResponse(**{**row, "value": "***encrypted***"}) for row in rows]


@router.get("/{secret_key}", response_model=SecretResponse)
async def get_secret(secret_key: str, request: Request):
    """Get a secret value by key (decrypts on read)."""
    row = await db.fetchone("SELECT * FROM secrets WHERE key = ?", (secret_key,))
    if not row:
        await _audit_log(secret_key, "read", ip=str(request.client.host) if request.client else "", success=False, details="Secret not found")
        raise EvershadeError.not_found(f"Secret {secret_key} not found")
    try:
        value = decrypt(row["encrypted_value"], row["iv"])
        await _audit_log(secret_key, "read", ip=str(request.client.host) if request.client else "")
        return SecretResponse(**{**row, "value": value})
    except Exception as e:
        await _audit_log(secret_key, "read", ip=str(request.client.host) if request.client else "", success=False, details=str(e))
        raise EvershadeError.internal_error("Failed to decrypt secret")


@router.post("", response_model=SecretResponse, status_code=201)
async def create_secret(secret: SecretCreate, request: Request):
    """Create a new encrypted secret."""
    # Check for duplicate key
    existing = await db.fetchone("SELECT id FROM secrets WHERE key = ?", (secret.key,))
    if existing:
        await _audit_log(secret.key, "create", ip=str(request.client.host) if request.client else "", success=False, details="Duplicate key")
        raise EvershadeError.conflict(f"Secret {secret.key} already exists")

    secret_id = str(uuid.uuid4())
    encrypted_value, iv, tag = encrypt(secret.value)

    await db.execute(
        """INSERT INTO secrets (id, key, encrypted_value, iv, tag, description)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (secret_id, secret.key, encrypted_value, iv, tag, secret.description),
    )
    await _audit_log(secret.key, "create", ip=str(request.client.host) if request.client else "")

    row = await db.fetchone("SELECT * FROM secrets WHERE id = ?", (secret_id,))
    return SecretResponse(**{**row, "value": secret.value})


@router.put("/{secret_key}", response_model=SecretResponse)
async def update_secret(secret_key: str, secret: SecretUpdate, request: Request):
    """Update an existing secret's value."""
    encrypted_value, iv, tag = encrypt(secret.value)

    updates = ["encrypted_value = ?", "iv = ?", "tag = ?", "value_placeholder = ?"]
    values = [encrypted_value, iv, tag, secret.value]

    if secret.description is not None:
        updates.append("description = ?")
        values.append(secret.description)

    updates.append("updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')")

    set_clause = ", ".join(updates)
    values.append(secret_key)

    existing = await db.fetchone("SELECT * FROM secrets WHERE key = ?", (secret_key,))
    if not existing:
        await _audit_log(secret_key, "update", ip=str(request.client.host) if request.client else "", success=False, details="Secret not found")
        raise EvershadeError.not_found(f"Secret {secret_key} not found")
    await db.execute(
        f"UPDATE secrets SET {set_clause} WHERE key = ?",
        values,
    )
    await _audit_log(secret_key, "update", ip=str(request.client.host) if request.client else "")

    row = await db.fetchone("SELECT * FROM secrets WHERE key = ?", (secret_key,))
    return SecretResponse(**{**row, "value": secret.value})


@router.delete("/{secret_key}", status_code=204)
async def delete_secret(secret_key: str, request: Request):
    """Delete a secret."""
    existing = await db.fetchone("SELECT * FROM secrets WHERE key = ?", (secret_key,))
    if not existing:
        await _audit_log(secret_key, "delete", ip=str(request.client.host) if request.client else "", success=False, details="Secret not found")
        raise EvershadeError.not_found(f"Secret {secret_key} not found")
    await db.execute("DELETE FROM secrets WHERE key = ?", (secret_key,))
    await _audit_log(secret_key, "delete", ip=str(request.client.host) if request.client else "")


@router.get("/audit", response_model=list[AuditLogResponse])
async def list_audit_log(
    secret_key: str | None = None,
    limit: int = 100,
):
    """List audit log entries."""
    if secret_key:
        rows = await db.fetchall(
            "SELECT * FROM audit_log WHERE secret_key = ? ORDER BY created_at DESC LIMIT ?",
            (secret_key, limit),
        )
    else:
        rows = await db.fetchall(
            "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
    return [AuditLogResponse(**{**row, "success": bool(row["success"])}) for row in rows]
