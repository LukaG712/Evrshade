"""Evershade Core — Shared platform foundation.

Provides configuration, error handling, health checks, telemetry,
middleware, authentication, and service discovery for all Evershade services.
"""

__version__ = "2.0.0"

from evershade.config import ServiceConfig, DatabaseConfig, TelemetryConfig, AuthConfig, Environment
from evershade.errors import (
    EvershadeError,
    ErrorCode,
    error_response,
    success_response,
    register_error_handlers,
    CorrelationIdMiddleware,
    RequestLoggingMiddleware,
)
from evershade.health import register_health_routes
from evershade.telemetry import setup_telemetry, create_traced_httpx_client
from evershade.auth import (
    create_service_token,
    verify_service_token,
    ServiceAuthMiddleware,
    require_service_auth,
)
from evershade.registry import (
    ServiceRegistry,
    ServiceStatus,
    register_service_routes,
    ServiceDiscoveryClient,
)

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
