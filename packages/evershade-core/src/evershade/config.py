"""Centralized configuration with Pydantic validation.

Every Evershade service loads its configuration through this module.
It provides:
- Environment variable loading with type coercion
- Schema validation at startup
- Environment-specific profiles (dev/staging/prod)
- Service-to-service URL resolution

Usage:
    from evershade.config import ServiceConfig
    config = ServiceConfig(service_name="Greenie", port=8080)
    print(config.log_level)  # From EVERSHADE_LOG_LEVEL or "INFO"
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Deployment environment."""

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class DatabaseConfig(BaseSettings):
    """Database connection settings."""

    model_config = SettingsConfigDict(env_prefix="DB_", env_nested_delimiter="__")

    url: str = Field(default="sqlite:///./app.db", description="Database URL")
    pool_size: int = Field(default=5, ge=1, le=20)
    max_overflow: int = Field(default=10, ge=0)
    echo: bool = Field(default=False, description="SQL logging")
    wal_mode: bool = Field(default=True, description="SQLite WAL mode")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v:
            raise ValueError("Database URL must not be empty")
        return v


class TelemetryConfig(BaseSettings):
    """OpenTelemetry and metrics configuration."""

    model_config = SettingsConfigDict(env_prefix="OTEL_", env_nested_delimiter="__")

    otlp_endpoint: str = Field(default="", description="OTLP collector endpoint")
    enabled: bool = Field(default=False)
    sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)

    @property
    def is_configured(self) -> bool:
        return bool(self.otlp_endpoint) or self.enabled


class AuthConfig(BaseSettings):
    """Service-to-service authentication settings."""

    model_config = SettingsConfigDict(env_prefix="AUTH_", env_nested_delimiter="__")

    jwt_secret: str = Field(default="", description="JWT signing secret")
    token_expiry_seconds: int = Field(default=3600, ge=60, le=86400)
    enabled: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_secret_required(self) -> AuthConfig:
        if self.enabled and not self.jwt_secret:
            raise ValueError("JWT secret is required when auth is enabled")
        return self


class ServiceConfig(BaseSettings):
    """Main configuration for an Evershade service.

    Reads from environment variables with the EVERSHADE_ prefix and
    falls back to sensible defaults. Validates all required fields
    at startup.

    Args:
        service_name: Human-readable service name (e.g. "Greenie").
        port: Default HTTP port for this service.
        version: Semantic version string.

    Examples:
        >>> config = ServiceConfig(service_name="Greenie", port=8080)
        >>> config.validate()  # Raises on invalid config
    """

    model_config = SettingsConfigDict(
        env_prefix="EVERSHADE_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_name: str = Field(..., min_length=1, max_length=64)
    port: int = Field(..., ge=1, le=65535)
    version: str = Field(default="2.0.0", min_length=1)
    environment: Environment = Field(default=Environment.DEV)
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    host: str = Field(default="0.0.0.0")

    # API key for external authentication
    api_key: str = Field(default="", description="Service API key")

    # Service-to-service URLs (resolved from Docker network)
    slinker_url: str = Field(default="http://Slinker:8000")
    trapper_url: str = Field(default="http://Trapper-api:3000")
    gobber_url: str = Field(default="http://Gobber:8085")
    sneaker_url: str = Field(default="http://Sneaker:8086")
    hider_url: str = Field(default="http://Hider:8087")
    poltergeist_url: str = Field(default="http://Poltergeist:8088")
    shrewd_url: str = Field(default="http://Shrewd:8089")
    greenie_url: str = Field(default="http://Greenie:8080")

    # Sub-configs
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)

    @field_validator("service_name")
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Service name must not be empty")
        allowed = {
            "Greenie",
            "Slinker",
            "Trapper",
            "Gobber",
            "Sneaker",
            "Hider",
            "Poltergeist",
            "Shrewd",
            "Slammer",
            "Speedy",
        }
        if v not in allowed:
            print(f"Warning: Unknown service name '{v}', expected one of {allowed}")
        return v

    def validate(self) -> dict[str, str]:
        """Validate configuration and return any warnings.

        Returns:
            Dictionary of warning messages (empty if config is valid).
        """
        warnings = {}

        if self.environment == Environment.PROD and not self.api_key:
            warnings["api_key"] = "API key is recommended in production"

        if self.environment == Environment.PROD and self.log_level == "DEBUG":
            warnings["log_level"] = "DEBUG logging is not recommended in production"

        if self.telemetry.is_configured and not self.telemetry.otlp_endpoint:
            warnings["telemetry"] = "Telemetry enabled but no OTLP endpoint configured"

        return warnings

    def dict_without_secrets(self) -> dict[str, Any]:
        """Return configuration dictionary with secrets redacted."""
        d = self.model_dump()
        if d.get("api_key"):
            d["api_key"] = "***REDACTED***"
        if d.get("auth", {}).get("jwt_secret"):
            d["auth"]["jwt_secret"] = "***REDACTED***"
        return d

    def __repr__(self) -> str:
        return (
            f"ServiceConfig(name={self.service_name!r}, "
            f"port={self.port}, "
            f"env={self.environment.value}, "
            f"version={self.version!r})"
        )
