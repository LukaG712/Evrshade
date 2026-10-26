"""Sneaker — Correlation and observability routes.

Endpoints for trace correlation, service health, AI observability,
Loki/Tempo integration, and Grafana dashboard data.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Request

from app.database import db
from app.correlation import ObservabilityCorrelator

router = APIRouter(prefix="/api/observe", tags=["observability"])


@router.get("/correlate/trace/{trace_id}")
async def correlate_by_trace(trace_id: str, request: Request) -> Dict[str, Any]:
    """Get all traces, logs, and metrics for a given trace_id."""
    correlator: ObservabilityCorrelator = request.app.state.correlator
    return await correlator.correlate_by_trace_id(trace_id)


@router.get("/correlate/service/{service_name}")
async def correlate_by_service(
    service_name: str,
    request: Request,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> Dict[str, Any]:
    """Get all activity for a service within a time window."""
    correlator: ObservabilityCorrelator = request.app.state.correlator
    return await correlator.correlate_by_service(service_name, start_time, end_time)


@router.get("/health")
async def get_service_health(request: Request) -> Dict[str, Any]:
    """Get health summary for all monitored services."""
    correlator: ObservabilityCorrelator = request.app.state.correlator
    return await correlator.get_service_health()


@router.get("/ai")
async def get_ai_observability(
    request: Request,
    model: Optional[str] = None,
    start_time: Optional[str] = None,
) -> Dict[str, Any]:
    """Get AI-specific observability data with Langfuse/Opik correlation."""
    correlator: ObservabilityCorrelator = request.app.state.correlator
    return await correlator.get_ai_observability(model, start_time)


@router.get("/loki/logs")
async def query_loki_logs(
    request: Request,
    query: str = "",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Query Loki for log aggregation."""
    correlator: ObservabilityCorrelator = request.app.state.correlator
    return await correlator.get_loki_logs(query, start_time, end_time, limit)


@router.get("/tempo/traces")
async def query_tempo_traces(
    request: Request,
    service_name: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """Query Tempo for distributed traces."""
    correlator: ObservabilityCorrelator = request.app.state.correlator
    return await correlator.get_tempo_traces(service_name, limit)


@router.get("/dashboard")
async def get_dashboard_data(request: Request) -> Dict[str, Any]:
    """Get aggregated data for Grafana dashboards."""
    correlator: ObservabilityCorrelator = request.app.state.correlator
    return await correlator.get_dashboard_data()
