"""OpenTelemetry instrumentation for Evershade services.

This module provides a reusable telemetry setup function for all Python services
in the Evershade ecosystem. It configures:
- FastAPI automatic instrumentation for HTTP server traces
- HTTPX automatic instrumentation for outgoing HTTP client traces
- OTLP exporter to send traces to Sneaker
- Prometheus metrics auto-instrumentation
- B3 trace context propagation across service boundaries

Usage:
    from evershade.telemetry import setup_telemetry, create_traced_httpx_client
    setup_telemetry(app, service_name="MyService")

    # For outgoing requests with trace context propagation:
    async with create_traced_httpx_client() as client:
        resp = await client.get("http://other-service/endpoint")

Traces are sent to the OTLP endpoint configured via SNEAKER_OTLP_ENDPOINT
environment variable. If not set, telemetry is disabled (no-op).
"""

from __future__ import annotations

import os

import httpx


def setup_telemetry(app, service_name: str = "evershade-service") -> None:
    """Set up OpenTelemetry instrumentation for an Evershade service.

    Configures trace collection, OTLP export, B3 propagation, and Prometheus
    metrics. Gracefully degrades when OpenTelemetry packages are unavailable
    or when no OTLP endpoint is configured.

    Args:
        app: FastAPI application instance.
        service_name: Name of the service for trace attributes.
    """
    otlp_endpoint = os.getenv("SNEAKER_OTLP_ENDPOINT")
    if not otlp_endpoint:
        _setup_prometheus_metrics(service_name)
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.propagate import set_global_textmap
        from opentelemetry.propagators.b3 import B3MultiFormat
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        _setup_prometheus_metrics(service_name)
        return

    # Set up trace provider
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Configure OTLP exporter
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    # Set up B3 propagation for trace context across service boundaries
    set_global_textmap(B3MultiFormat())

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(
        app,
        server_request_hook=lambda span, request: _server_request_hook(
            span, request, service_name
        ),
    )

    # Instrument HTTPX for outgoing requests
    HTTPXClientInstrumentor.instrument()

    # Set up Prometheus metrics
    _setup_prometheus_metrics(service_name)


def create_traced_httpx_client(
    base_url: str | None = None,
    timeout: float = 30.0,
) -> httpx.AsyncClient:
    """Create an HTTPX async client that propagates OpenTelemetry trace context.

    This client automatically injects B3 trace headers into outgoing requests,
    enabling distributed tracing across service boundaries.

    Args:
        base_url: Optional base URL for the client.
        timeout: Request timeout in seconds.

    Returns:
        Configured httpx.AsyncClient instance.
    """
    kwargs: dict = {"timeout": timeout}
    if base_url is not None:
        kwargs["base_url"] = base_url
    client = httpx.AsyncClient(**kwargs)

    # If OpenTelemetry is available, headers are injected automatically
    # by the HTTPXClientInstrumentor. If not, the client still works normally.
    return client


def _setup_prometheus_metrics(service_name: str) -> None:
    """Set up Prometheus metrics auto-instrumentation.

    Registers standard HTTP request counters and histograms.
    The metrics are exposed via the /metrics endpoint in evershade_health.

    Args:
        service_name: Name of the service for metric labels.
    """
    try:
        import prometheus_client
        from prometheus_client import Counter, Histogram

        # Check if we've already set up metrics (avoid duplicates)
        if hasattr(_setup_prometheus_metrics, "_initialized"):
            return
        _setup_prometheus_metrics._initialized = True

        # HTTP request counter
        prometheus_client.REGISTRY.register(
            Counter(
                f"{service_name.lower()}_http_requests_total",
                f"Total HTTP requests to {service_name}",
                ["method", "endpoint", "status"],
            )
        )

        # HTTP request duration histogram
        prometheus_client.REGISTRY.register(
            Histogram(
                f"{service_name.lower()}_http_request_duration_seconds",
                f"HTTP request duration for {service_name}",
                ["method", "endpoint"],
                buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0),
            )
        )

    except (ImportError, Exception):
        # Metrics setup should not crash the service
        pass


def _server_request_hook(span, request, service_name: str) -> None:
    """Add semantic attributes to server request spans."""
    if not span.is_recording():
        return

    span.set_attribute("service.name", service_name)
    span.set_attribute("http.route", request.url.path)
