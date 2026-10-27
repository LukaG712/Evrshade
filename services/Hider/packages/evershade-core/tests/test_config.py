"""Tests for evershade.config — Configuration validation."""

import pytest
from evershade.config import (
    AuthConfig,
    DatabaseConfig,
    Environment,
    ServiceConfig,
    TelemetryConfig,
)
from pydantic import ValidationError


class TestServiceConfig:
    """Test ServiceConfig loading and validation."""

    def test_default_config(self):
        """Config loads with defaults."""
        config = ServiceConfig(service_name="Greenie", port=8080)
        assert config.service_name == "Greenie"
        assert config.port == 8080
        assert config.version == "2.0.0"
        assert config.environment == Environment.DEV
        assert config.log_level == "INFO"

    def test_env_variable_override(self, monkeypatch):
        """Environment variables override defaults."""
        monkeypatch.setenv("EVERSHADE_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("EVERSHADE_ENVIRONMENT", "prod")
        config = ServiceConfig(service_name="Slinker", port=8000)
        assert config.log_level == "DEBUG"
        assert config.environment == Environment.PROD

    def test_invalid_log_level(self):
        """Invalid log level raises ValidationError."""
        with pytest.raises(ValidationError):
            ServiceConfig(service_name="Greenie", port=8080, log_level="INVALID")

    def test_port_range(self):
        """Port must be in valid range."""
        with pytest.raises(ValidationError):
            ServiceConfig(service_name="Greenie", port=0)
        with pytest.raises(ValidationError):
            ServiceConfig(service_name="Greenie", port=70000)

    def test_empty_service_name(self):
        """Empty service name raises ValidationError."""
        with pytest.raises(ValidationError):
            ServiceConfig(service_name="", port=8080)

    def test_validate_warnings(self):
        """validate() returns warnings for production config."""
        config = ServiceConfig(
            service_name="Greenie",
            port=8080,
            environment=Environment.PROD,
            log_level="DEBUG",
        )
        warnings = config.validate()
        assert "api_key" in warnings
        assert "log_level" in warnings

    def test_dict_without_secrets(self):
        """Secrets are redacted in dict output."""
        config = ServiceConfig(
            service_name="Greenie",
            port=8080,
            api_key="secret-key",
        )
        d = config.dict_without_secrets()
        assert d["api_key"] == "***REDACTED***"

    def test_service_urls(self):
        """Service URLs have correct defaults."""
        config = ServiceConfig(service_name="Greenie", port=8080)
        assert config.slinker_url == "http://Slinker:8000"
        assert config.shrewd_url == "http://Shrewd:8089"

    def test_repr(self):
        """__repr__ returns readable string."""
        config = ServiceConfig(service_name="Greenie", port=8080)
        assert "Greenie" in repr(config)
        assert "8080" in repr(config)


class TestDatabaseConfig:
    """Test DatabaseConfig validation."""

    def test_default_db_config(self):
        """Database config loads with defaults."""
        config = DatabaseConfig()
        assert config.wal_mode is True
        assert config.pool_size == 5

    def test_empty_url(self):
        """Empty URL raises ValidationError."""
        with pytest.raises(ValidationError):
            DatabaseConfig(url="")


class TestTelemetryConfig:
    """Test TelemetryConfig."""

    def test_is_configured(self):
        """is_configured returns True when endpoint is set."""
        config = TelemetryConfig(otlp_endpoint="http://sneaker:8086")
        assert config.is_configured is True

        config2 = TelemetryConfig()
        assert config2.is_configured is False


class TestAuthConfig:
    """Test AuthConfig validation."""

    def test_secret_required_when_enabled(self):
        """JWT secret is required when auth is enabled."""
        with pytest.raises(ValidationError):
            AuthConfig(enabled=True, jwt_secret="")

    def test_disabled_without_secret(self):
        """Auth can be disabled without a secret."""
        config = AuthConfig(enabled=False, jwt_secret="")
        assert config.enabled is False
