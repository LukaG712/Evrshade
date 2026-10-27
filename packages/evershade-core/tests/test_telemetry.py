"""Tests for evershade.telemetry module.

Tests cover:
- setup_telemetry without OTLP endpoint (Prometheus-only mode)
- setup_telemetry with missing OpenTelemetry packages (graceful degradation)
- create_traced_httpx_client creation
- Prometheus metrics setup
- Server request hook
"""

import os
from unittest.mock import MagicMock, patch

from evershade.telemetry import (
    _server_request_hook,
    _setup_prometheus_metrics,
    create_traced_httpx_client,
    setup_telemetry,
)


class TestSetupTelemetry:
    """Test telemetry setup function."""

    def test_setup_without_otlp_endpoint(self):
        """Without SNEAKER_OTLP_ENDPOINT, only Prometheus metrics are set up."""
        # Reset the Prometheus init flag and mock REGISTRY to avoid duplicates
        if hasattr(_setup_prometheus_metrics, "_initialized"):
            delattr(_setup_prometheus_metrics, "_initialized")
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("prometheus_client.REGISTRY.register"),
        ):
            app = MagicMock()
            setup_telemetry(app, service_name="TestService")
            # Should not raise, should set up Prometheus metrics only

    def test_setup_with_missing_opentelemetry(self):
        """When OpenTelemetry packages are missing, degrade gracefully."""
        with (
            patch.dict(os.environ, {"SNEAKER_OTLP_ENDPOINT": "http://sneaker:8086"}),
            patch(
                "sys.modules",
                {
                    "opentelemetry": None,
                    "opentelemetry.exporter.otlp.proto.grpc.trace_exporter": None,
                },
            ),
        ):
            app = MagicMock()
            # Should not raise even with missing packages
            setup_telemetry(app, service_name="TestService")

    def test_setup_with_otlp_endpoint(self):
        """With SNEAKER_OTLP_ENDPOINT, full OTLP setup is configured."""
        with patch.dict(os.environ, {"SNEAKER_OTLP_ENDPOINT": "http://sneaker:8086"}):
            # Mock the imports inside setup_telemetry's try block
            mock_trace = MagicMock()
            mock_trace_module = MagicMock()
            mock_trace_module.trace = mock_trace

            mock_exporter_class = MagicMock()
            mock_processor_class = MagicMock()
            mock_provider_class = MagicMock()
            mock_instrumentor_fastapi = MagicMock()
            mock_instrumentor_httpx = MagicMock()
            mock_set_global_textmap = MagicMock()
            mock_b3 = MagicMock()

            mocked_modules = {
                "opentelemetry": mock_trace_module,
                "opentelemetry.exporter.otlp.proto.grpc.trace_exporter": MagicMock(
                    OTLPSpanExporter=mock_exporter_class
                ),
                "opentelemetry.instrumentation.fastapi": MagicMock(FastAPIInstrumentor=mock_instrumentor_fastapi),
                "opentelemetry.instrumentation.httpx": MagicMock(HTTPXClientInstrumentor=mock_instrumentor_httpx),
                "opentelemetry.propagate": MagicMock(set_global_textmap=mock_set_global_textmap),
                "opentelemetry.propagators.b3": MagicMock(B3MultiFormat=mock_b3),
                "opentelemetry.sdk.trace": MagicMock(TracerProvider=mock_provider_class),
                "opentelemetry.sdk.trace.export": MagicMock(BatchSpanProcessor=mock_processor_class),
            }

            with patch.dict("sys.modules", mocked_modules):
                app = MagicMock()
                setup_telemetry(app, service_name="TestService")
                # Verify OTLP exporter was created with correct endpoint
                mock_exporter_class.assert_called_once_with(endpoint="http://sneaker:8086", insecure=True)

    def test_setup_resets_prometheus_flag(self):
        """Prometheus metrics initialization flag prevents duplicates."""
        # Remove the flag if it exists
        if hasattr(_setup_prometheus_metrics, "_initialized"):
            delattr(_setup_prometheus_metrics, "_initialized")

        with patch("prometheus_client.REGISTRY.register") as mock_register:
            _setup_prometheus_metrics("TestSvc")
            call_count_first = mock_register.call_count

            # Second call should be a no-op
            _setup_prometheus_metrics("TestSvc")
            call_count_second = mock_register.call_count

            assert call_count_first == call_count_second


class TestCreateTracedHttpxClient:
    """Test HTTPX client creation."""

    def test_create_client_default(self):
        """Create client with default settings."""
        client = create_traced_httpx_client()
        assert client is not None

    def test_create_client_with_base_url(self):
        """Create client with custom base URL."""
        client = create_traced_httpx_client(base_url="http://test:8000")
        assert client is not None
        assert "test:8000" in str(client.base_url)

    def test_create_client_with_timeout(self):
        """Create client with custom timeout."""
        client = create_traced_httpx_client(timeout=60.0)
        assert client is not None


class TestServerRequestHook:
    """Test server request span hook."""

    def test_hook_sets_attributes(self):
        """Hook sets service.name and http.route attributes."""
        span = MagicMock()
        span.is_recording.return_value = True
        request = MagicMock()
        request.url.path = "/api/test"

        _server_request_hook(span, request, "TestService")

        span.set_attribute.assert_any_call("service.name", "TestService")
        span.set_attribute.assert_any_call("http.route", "/api/test")

    def test_hook_skips_non_recording_span(self):
        """Hook does nothing when span is not recording."""
        span = MagicMock()
        span.is_recording.return_value = False
        request = MagicMock()

        _server_request_hook(span, request, "TestService")

        span.set_attribute.assert_not_called()
