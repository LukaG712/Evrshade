"""OpenTelemetry instrumentation for Evershade services.

This module provides a reusable telemetry setup function for all Python services
in the Evershade ecosystem. It configures:
- FastAPI automatic instrumentation for HTTP server traces
- HTTPX automatic instrumentation for outgoing HTTP client traces
- OTLP exporter to send traces to Sneaker

Usage:
    from evershade_telemetry import setup_telemetry
    setup_telemetry(app, service_name="MyService")

Traces are sent to the OTLP endpoint configured via SNEAKER_OTLP_ENDPOINT
environment variable. If not set, telemetry is disabled (no-op).
"""

import os


def setup_telemetry(app, service_name: str = "evershade-service") -> None:
    """Set up OpenTelemetry instrumentation for an Evershade service.

    Args:
        app: FastAPI application instance
        service_name: Name of the service for trace attributes
    """
    otlp_endpoint = os.getenv("SNEAKER_OTLP_ENDPOINT")
    if not otlp_endpoint:
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
        return

    # Set up trace provider
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Configure OTLP exporter
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    # Set up B3 propagation for trace context
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


def _server_request_hook(span, request, service_name: str) -> None:
    """Add semantic attributes to server request spans."""
    if not span.is_recording():
        return

    span.set_attribute("service.name", service_name)
    span.set_attribute("http.route", request.url.path)
