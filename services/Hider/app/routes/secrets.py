"""Hider — Secrets management routes."""

from __future__ import annotations

import base64
import hashlib
import os
import re

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from fastapi import APIRouter, HTTPException

from app.database import db
from app.models import SecretCreate, SecretResponse, SecretUpdate, gen_id

router = APIRouter()

# Encryption key from environment
_ENCRYPTION_KEY_RAW = os.getenv("ENCRYPTION_KEY", "")
if not _ENCRYPTION_KEY_RAW:
    raise RuntimeError(
        "ENCRYPTION_KEY environment variable is not set. Refusing to start Hider without an encryption key."
    )

# Encryption salt — required for key derivation
_ENCRYPTION_SALT_RAW = os.getenv("ENCRYPTION_SALT", "")
if not _ENCRYPTION_SALT_RAW:
    raise RuntimeError(
        "ENCRYPTION_SALT environment variable is not set. Refusing to start Hider without an encryption salt. "
        "Generate one: openssl rand -hex 16"
    )
# Reject known default salts
if _ENCRYPTION_SALT_RAW.lower() in ("evershade-hider-salt-v1", "change-me", "default", "test", "salt"):
    raise RuntimeError(
        "ENCRYPTION_SALT is using a known default value. Generate a random salt: openssl rand -hex 16"
    )

# Derive a 32-byte key using PBKDF2-HMAC-SHA256 with 100k iterations
# This is much more secure than plain SHA-256 hashing
try:
    salt_bytes = bytes.fromhex(_ENCRYPTION_SALT_RAW)
except ValueError:
    salt_bytes = _ENCRYPTION_SALT_RAW.encode()

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt_bytes,
    iterations=100_000,
)
_ENCRYPTION_KEY = kdf.derive(_ENCRYPTION_KEY_RAW.encode())


def _validate_secret_name(name: str) -> None:
    """Validate secret name to prevent path traversal and other injection attacks.

    Args:
        name: The secret name to validate.

    Raises:
        HTTPException: If the name is invalid.
    """
    if not name:
        raise HTTPException(status_code=400, detail="Secret name cannot be empty")
    if len(name) > 255:
        raise HTTPException(status_code=400, detail="Secret name is too long (max 255 characters)")
    # Reject path traversal, null bytes, and control characters
    if ".." in name or "\x00" in name:
        raise HTTPException(status_code=400, detail="Secret name contains invalid characters")
    # Only allow alphanumeric, hyphens, underscores, dots, and slashes (for namespacing)
    if not re.match(r'^[a-zA-Z0-9._/-]+$', name):
        raise HTTPException(
            status_code=400,
            detail="Secret name can only contain alphanumeric characters, hyphens, underscores, dots, and slashes"
        )


def encrypt_value(plaintext: str) -> tuple[str, str, str]:
    """Encrypt a value using AES-256-GCM. Returns (encrypted_value, iv, tag)."""
    aesgcm = AESGCM(_ENCRYPTION_KEY)
    iv = os.urandom(12)
    ciphertext = aesgcm.encrypt(iv, plaintext.encode(), None)
    return (
        base64.b64encode(ciphertext).decode(),
        base64.b64encode(iv).decode(),
        "",
    )


def decrypt_value(encrypted: str, iv: str) -> str:
    """Decrypt a value using AES-256-GCM."""
    aesgcm = AESGCM(_ENCRYPTION_KEY)
    ciphertext = base64.b64decode(encrypted)
    iv_bytes = base64.b64decode(iv)
    plaintext = aesgcm.decrypt(iv_bytes, ciphertext, None)
    return plaintext.decode()


async def _log_audit(action: str, resource_type: str, resource_id: str) -> None:
    """Log an audit entry."""
    await db.execute(
        "INSERT INTO audit_log (id, action, resource_type, resource_id) VALUES (?, ?, ?, ?)",
        (gen_id(), action, resource_type, resource_id),
    )


@router.post("/", status_code=201)
async def create_secret(secret: SecretCreate) -> SecretResponse:
    """Create a new encrypted secret."""
    _validate_secret_name(secret.name)
    sid = gen_id()
    encrypted, iv, _ = encrypt_value(secret.value)
    await db.execute(
        "INSERT INTO secrets (id, name, encrypted_value, iv, tag, description) VALUES (?, ?, ?, ?, ?, ?)",
        (sid, secret.name, encrypted, iv, "", secret.description),
    )
    # Log history
    await db.execute(
        "INSERT INTO secret_history (id, secret_id, encrypted_value, iv, tag, version, action) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (gen_id(), sid, encrypted, iv, "", 1, "created"),
    )
    await _log_audit("create", "secret", sid)
    row = await db.fetchone("SELECT * FROM secrets WHERE id = ?", (sid,))
    return SecretResponse(**row)


@router.get("/")
async def list_secrets() -> list[SecretResponse]:
    """List all secrets (without values)."""
    rows = await db.fetchall("SELECT * FROM secrets ORDER BY name")
    return [SecretResponse(**r) for r in rows]


@router.get("/{secret_id}")
async def get_secret(secret_id: str) -> dict:
    """Get a secret by ID, returning the decrypted value."""
    row = await db.fetchone("SELECT * FROM secrets WHERE id = ?", (secret_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Secret not found")
    value = decrypt_value(row["encrypted_value"], row["iv"])
    await _log_audit("read", "secret", secret_id)
    return {
        "id": row["id"],
        "name": row["name"],
        "value": value,
        "description": row["description"],
        "version": row["version"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.put("/{secret_id}")
async def update_secret(secret_id: str, update: SecretUpdate) -> dict:
    """Update a secret's value."""
    row = await db.fetchone("SELECT * FROM secrets WHERE id = ?", (secret_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Secret not found")
    new_version = row["version"] + 1
    encrypted, iv, _ = encrypt_value(update.value)
    await db.execute(
        "UPDATE secrets SET encrypted_value = ?, iv = ?, tag = ?, version = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE id = ?",
        (encrypted, iv, "", new_version, secret_id),
    )
    await db.execute(
        "INSERT INTO secret_history (id, secret_id, encrypted_value, iv, tag, version, action) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (gen_id(), secret_id, encrypted, iv, "", new_version, "updated"),
    )
    await _log_audit("update", "secret", secret_id)
    value = decrypt_value(encrypted, iv)
    return {
        "id": secret_id,
        "name": row["name"],
        "value": value,
        "version": new_version,
    }


@router.delete("/{secret_id}", status_code=204)
async def delete_secret(secret_id: str) -> None:
    """Delete a secret."""
    row = await db.fetchone("SELECT * FROM secrets WHERE id = ?", (secret_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Secret not found")
    await db.execute("DELETE FROM secrets WHERE id = ?", (secret_id,))
    await _log_audit("delete", "secret", secret_id)
