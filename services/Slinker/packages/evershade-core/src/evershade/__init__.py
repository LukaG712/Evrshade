"""Evershade Core — Shared platform foundation.

Provides configuration, error handling, health checks, telemetry,
middleware, authentication, and service discovery for all Evershade services.
"""

__version__ = "2.0.0"

from evershade.auth import (
    ServiceAuthMiddleware,
    create_service_token,
    require_service_auth,
    verify_service_token,
)
from evershade.config import (
    AuthConfig,
    DatabaseConfig,
    Environment,
    ServiceConfig,
    TelemetryConfig,
)
from evershade.errors import (
    CorrelationIdMiddleware,
    ErrorCode,
    EvershadeError,
    RequestLoggingMiddleware,
    error_response,
    register_error_handlers,
    success_response,
)
from evershade.health import register_health_routes
from evershade.registry import (
    ServiceDiscoveryClient,
    ServiceRegistry,
    ServiceStatus,
    register_service_routes,
)
from evershade.telemetry import create_traced_httpx_client, setup_telemetry

__all__ = [
    # Config
    "ServiceConfig",
    "DatabaseConfig",
    "TelemetryConfig",
    "AuthConfig",
    "Environment",
    # Errors
    "EvershadeError",
    "ErrorCode",
    "error_response",
    "success_response",
    "register_error_handlers",
    "CorrelationIdMiddleware",
    "RequestLoggingMiddleware",
    # Health
    "register_health_routes",
    # Telemetry
    "setup_telemetry",
    "create_traced_httpx_client",
    # Auth
    "create_service_token",
    "verify_service_token",
    "ServiceAuthMiddleware",
    "require_service_auth",
    # Registry
    "ServiceRegistry",
    "ServiceStatus",
    "register_service_routes",
    "ServiceDiscoveryClient",
]
