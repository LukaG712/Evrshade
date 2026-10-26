"""Greenie — API key authentication middleware.

Validates Bearer tokens against stored API keys.
Service-to-service calls use the EVERSHADE_SERVICE_API_KEY.

Usage:

    from app.auth import require_api_key, verify_api_key
"""

from __future__ import annotations

import hashlib
import os
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from evershade_error import ErrorCode

from app.database import get_db_instance

# Service API key for internal communication
SERVICE_API_KEY = os.getenv("EVERSHADE_SERVICE_API_KEY", "")

security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """Verify the API key and return the user ID.

    Returns:
        User ID associated with the API key.

    Raises:
        HTTPException: 401 if the API key is invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={
                "error": ErrorCode.UNAUTHORIZED.value,
                "message": "Missing API key",
            },
        )

    key = credentials.credentials

    # Allow service-to-service calls with the shared key
    if SERVICE_API_KEY and key == SERVICE_API_KEY:
        return "service"

    # Look up the key in the database
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    async for db in get_db_instance():
        row = await db.fetch_one(
            "SELECT id, user_id FROM api_keys WHERE key_hash = ? AND active = 1",
            (key_hash,),
        )
        if row:
            # Update last used time
            await db.execute(
                "UPDATE api_keys SET last_used_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE id = ?",
                (row["id"],),
            )
            return row["user_id"]

    raise HTTPException(
        status_code=401,
        detail={
            "error": ErrorCode.UNAUTHORIZED.value,
            "message": "Invalid API key",
        },
    )


async def optional_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """Optional API key verification — returns None if no key is provided.

    Returns:
        User ID if valid, None otherwise.
    """
    if credentials is None:
        return None

    key = credentials.credentials
    if SERVICE_API_KEY and key == SERVICE_API_KEY:
        return "service"

    key_hash = hashlib.sha256(key.encode()).hexdigest()
    async for db in get_db_instance():
        row = await db.fetch_one(
            "SELECT user_id FROM api_keys WHERE key_hash = ? AND active = 1",
            (key_hash,),
        )
        if row:
            return row["user_id"]

    return None


def require_api_key():
    """Dependency that requires a valid API key."""
    return verify_api_key


def optional_auth():
    """Dependency that optionally authenticates the request."""
    return optional_api_key
