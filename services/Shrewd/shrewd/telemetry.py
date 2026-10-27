"""OpenTelemetry instrumentation for Shrewd service."""

import os


def setup_telemetry(app) -> None:
    """Set up OpenTelemetry instrumentation for the Shrewd service.

    Configures:
    - FastAPI automatic instrumentation for HTTP server traces
    - HTTPX automatic instrumentation for outgoing HTTP client traces
    - OTLP exporter to send traces to Sneaker

    Traces are sent to the OTLP endpoint configured via SNEAKER_OTLP_ENDPOINT
    environment variable. If not set, telemetry is disabled.
    """
    otlp_endpoint = os.getenv("SNEAKER_OTLP_ENDPOINT")
    if not otlp_endpoint:
        return

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.propagate import set_global_textmap
    from opentelemetry.propagators.b3 import B3MultiFormat
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

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
        server_request_hook=_server_request_hook,
    )

    # Instrument HTTPX for outgoing requests
    HTTPXClientInstrumentor.instrument()


def _server_request_hook(span, request) -> None:
    """Add semantic attributes to server request spans."""
    if not span.is_recording():
        return

    # Add service-specific attributes
    span.set_attribute("service.name", "Shrewd")
    span.set_attribute("http.route", request.url.path)
