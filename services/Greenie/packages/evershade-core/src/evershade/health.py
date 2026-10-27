"""Shared health check endpoints for Evershade services.

Provides standard liveness, readiness, status, and metrics endpoints
that every service exposes. Import and register with any FastAPI application:

    from evershade.health import register_health_routes
    register_health_routes(app, service_name="MyService", version="2.0.0")
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Response


def register_health_routes(
    app,
    service_name: str,
    version: str = "2.0.0",
    dependencies: list[str] | None = None,
) -> None:
    """Register standard health check routes on a FastAPI application.

    Args:
        app: FastAPI application instance.
        service_name: Human-readable service name.
        version: Semantic version string.
        dependencies: Optional list of dependency service names for /ready checks.
    """
    router = APIRouter(tags=["health"])

    _start_time = datetime.now(UTC)
    _ready = True
    _request_count = 0

    @router.get("/health")
    async def health():
        """Liveness check — returns 200 if the process is running."""
        nonlocal _request_count
        _request_count += 1
        return {
            "status": "ok",
            "service": service_name,
            "version": version,
        }

    @router.get("/ready")
    async def ready():
        """Readiness check — returns 200 if fully initialized."""
        nonlocal _request_count
        _request_count += 1
        if not _ready:
            return {"status": "not_ready", "service": service_name}
        return {"status": "ready", "service": service_name}

    @router.get("/api/status")
    async def status():
        """Detailed status — version, uptime, capabilities, dependency health."""
        nonlocal _request_count
        _request_count += 1
        now = datetime.now(UTC)
        uptime_seconds = (now - _start_time).total_seconds()

        result = {
            "service": service_name,
            "version": version,
            "status": "running",
            "uptimeSeconds": round(uptime_seconds, 1),
            "startTime": _start_time.isoformat(),
            "dependencies": {},
        }

        if dependencies:
            for dep in dependencies:
                result["dependencies"][dep] = "unknown"

        return result

    @router.get("/metrics")
    async def metrics():
        """Prometheus-compatible metrics endpoint."""
        nonlocal _request_count
        _request_count += 1
        now = datetime.now(UTC)
        uptime_seconds = (now - _start_time).total_seconds()

        try:
            from prometheus_client import REGISTRY, generate_latest

            body = generate_latest(REGISTRY).decode("utf-8")
            return Response(
                content=body,
                media_type="text/plain; version=0.0.4",
            )
        except ImportError:
            body = (
                f"# HELP {service_name}_uptime_seconds Service uptime in seconds.\n"
                f"# TYPE {service_name}_uptime_seconds gauge\n"
                f"{service_name}_uptime_seconds {uptime_seconds:.1f}\n"
                f"# HELP {service_name}_requests_total Total HTTP requests.\n"
                f"# TYPE {service_name}_requests_total counter\n"
                f"{service_name}_requests_total {_request_count}\n"
                f"# HELP {service_name}_ready Service readiness (1=ready, 0=not ready).\n"
                f"# TYPE {service_name}_ready gauge\n"
                f"{service_name}_ready {1 if _ready else 0}\n"
            )
            return Response(
                content=body,
                media_type="text/plain; version=0.0.4",
            )

    app.include_router(router)
