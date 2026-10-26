"""Standard error response envelope for Evershade services.

Every service returns errors in a consistent JSON format:

    {
      "success": false,
      "data": null,
      "error": {
        "code": "VALIDATION_ERROR",
        "message": "Human-readable description",
        "details": "Optional technical context"
      },
      "requestId": "uuid",
      "timestamp": "2026-10-26T10:00:00Z"
    }

Usage:

    from evershade_error import error_response, EvershadeError, ErrorCode
    raise EvershadeError(ErrorCode.NOT_FOUND, "Agent not found", agent_id="abc")
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    """Standard error codes for Evershade services."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# Map error codes to HTTP status codes
ERROR_CODE_TO_STATUS = {
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
    ErrorCode.INTERNAL_ERROR: 500,
}


class EvershadeError(Exception):
    """Application-level error with structured payload.

    Args:
        code: Standard error code.
        message: Human-readable description.
        details: Optional technical context (dict or string).
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        details: Any | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details
        super().__init__(f"{code.value}: {message}")


def error_response(
    code: ErrorCode,
    message: str,
    *,
    details: Any | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """Build a standard error response envelope.

    Args:
        code: Standard error code.
        message: Human-readable description.
        details: Optional technical context.
        request_id: Optional request UUID; auto-generated if not provided.

    Returns:
        Dictionary matching the standard error response format.
    """
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code.value,
            "message": message,
            "details": details,
        },
        "requestId": request_id or str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
    }


def success_response(
    data: Any,
    *,
    request_id: str | None = None,
) -> dict[str, Any]:
    """Build a standard success response envelope.

    Args:
        data: The response payload.
        request_id: Optional request UUID; auto-generated if not provided.

    Returns:
        Dictionary matching the standard success response format.
    """
    return {
        "success": True,
        "data": data,
        "error": None,
        "requestId": request_id or str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
    }
