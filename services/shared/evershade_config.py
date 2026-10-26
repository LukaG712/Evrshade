"""Shared configuration loading for Evershade services.

Loads environment variables with sensible defaults and validation.
Every Python service imports this module to get its configuration.

Usage:

    from evershade_config import ServiceConfig
    config = ServiceConfig("MyService", port=8080)
    print(config.log_level)   # From EVERSHADE_LOG_LEVEL or "INFO"
    print(config.port)        # 8080
"""

from __future__ import annotations

import os
from typing import Optional


class ServiceConfig:
    """Configuration for a single Evershade service.

    Reads from environment variables with the EVERSHADE_ prefix and
    falls back to sensible defaults.

    Args:
        service_name: Human-readable service name (e.g. "Greenie").
        port: Default HTTP port for this service.
        api_key_env: Environment variable name for the service API key.
    """

    def __init__(
        self,
        service_name: str,
        port: int,
        *,
        api_key_env: Optional[str] = None,
    ) -> None:
        self.service_name = service_name
        self.port = port
        self.log_level = os.getenv("EVERSHADE_LOG_LEVEL", "INFO")
        self.otlp_endpoint = os.getenv("SNEAKER_OTLP_ENDPOINT", "")

        # API key: use the provided env var name, or fall back to
        # EVERSHADE_<SERVICE>_API_KEY pattern.
        if api_key_env:
            self.api_key = os.getenv(api_key_env, "")
        else:
            env_name = f"EVERSHADE_{service_name.upper()}_API_KEY"
            self.api_key = os.getenv(env_name, "")

    @property
    def has_otlp(self) -> bool:
        """Whether OpenTelemetry tracing is configured."""
        return bool(self.otlp_endpoint)

    @property
    def has_api_key(self) -> bool:
        """Whether an API key is configured."""
        return bool(self.api_key)

    def __repr__(self) -> str:
        return (
            f"ServiceConfig(name={self.service_name!r}, "
            f"port={self.port}, "
            f"log_level={self.log_level!r})"
        )
