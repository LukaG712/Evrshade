"""Sneaker — Observability correlation and aggregation.

Provides:
- Trace correlation across services using trace_id
- Log aggregation with Loki integration
- Tempo trace integration
- Langfuse/Opik AI observability correlation
- Grafana dashboard provisioning
- Cross-service activity correlation
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from evershade_db import Database

logger = logging.getLogger(__name__)


class ObservabilityCorrelator:
    """Correlate traces, logs, and metrics across services."""

    def __init__(self, db: Database, http_client: Any):
        self.db = db
        self.http_client = http_client

    async def correlate_by_trace_id(
        self,
        trace_id: str,
    ) -> Dict[str, Any]:
        """Get all traces, logs, and metrics for a given trace_id."""
        # Get traces
        traces = await self.db.fetchall(
            "SELECT * FROM traces WHERE trace_id = ? ORDER BY start_time",
            (trace_id,),
        )

        # Get logs
        logs = await self.db.fetchall(
            "SELECT * FROM logs WHERE trace_id = ? ORDER BY timestamp",
            (trace_id,),
        )

        # Get metrics for services involved in this trace
        services = set()
        for trace in traces:
            services.add(trace["service_name"])

        metrics = []
        for service in services:
            service_metrics = await self.db.fetchall(
                "SELECT * FROM metrics WHERE service_name = ? ORDER BY timestamp DESC LIMIT 10",
                (service,),
            )
            metrics.extend(service_metrics)

        return {
            "trace_id": trace_id,
            "traces": traces,
            "logs": logs,
            "metrics": metrics,
            "services": list(services),
            "span_count": len(traces),
            "log_count": len(logs),
        }

    async def correlate_by_service(
        self,
        service_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all activity for a service within a time window."""
        time_filter = ""
        params = [service_name]

        if start_time:
            time_filter += " AND created_at >= ?"
            params.append(start_time)
        if end_time:
            time_filter += " AND created_at <= ?"
            params.append(end_time)

        # Get traces
        traces = await self.db.fetchall(
            f"SELECT * FROM traces WHERE service_name = ?{time_filter} ORDER BY start_time DESC LIMIT 100",
            params,
        )

        # Get logs
        logs = await self.db.fetchall(
            f"SELECT * FROM logs WHERE service_name = ?{time_filter} ORDER BY timestamp DESC LIMIT 100",
            params,
        )

        # Get metrics
        metrics = await self.db.fetchall(
            f"SELECT * FROM metrics WHERE service_name = ?{time_filter} ORDER BY timestamp DESC LIMIT 50",
            params,
        )

        # Get alert history
        alerts = await self.db.fetchall(
            "SELECT ah.*, ar.name as rule_name "
            "FROM alert_history ah "
            "JOIN alert_rules ar ON ah.rule_id = ar.id "
            "WHERE ar.enabled = 1 "
            "ORDER BY ah.triggered_at DESC LIMIT 20",
        )

        return {
            "service_name": service_name,
            "traces": traces,
            "logs": logs,
            "metrics": metrics,
            "alerts": alerts,
            "trace_count": len(traces),
            "log_count": len(logs),
            "metric_count": len(metrics),
        }

    async def get_service_health(
        self,
    ) -> Dict[str, Any]:
        """Get health summary for all monitored services."""
        services = await self.db.fetchall(
            "SELECT DISTINCT service_name FROM traces ORDER BY service_name"
        )

        health = {}
        for svc in services:
            service_name = svc["service_name"]

            # Recent error rate
            recent_traces = await self.db.fetchall(
                """SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'ERROR' THEN 1 ELSE 0 END) as errors
                FROM traces
                WHERE service_name = ?
                AND created_at >= datetime('now', '-1 hour')""",
                (service_name,),
            )

            # Recent log errors
            recent_logs = await self.db.fetchall(
                """SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN level IN ('error', 'critical') THEN 1 ELSE 0 END) as errors
                FROM logs
                WHERE service_name = ?
                AND timestamp >= datetime('now', '-1 hour')""",
                (service_name,),
            )

            # Active alerts
            active_alerts = await self.db.fetchall(
                """SELECT COUNT(*) as cnt
                FROM alert_history ah
                JOIN alert_rules ar ON ah.rule_id = ar.id
                WHERE ah.triggered_at >= datetime('now', '-15 minutes')""",
            )

            total_traces = recent_traces[0]["total"] if recent_traces else 0
            error_traces = recent_traces[0]["errors"] if recent_traces and recent_traces[0]["errors"] else 0
            error_rate = (error_traces / total_traces * 100) if total_traces > 0 else 0

            health[service_name] = {
                "total_traces_1h": total_traces,
                "error_traces_1h": error_traces,
                "error_rate_percent": round(error_rate, 2),
                "total_logs_1h": recent_logs[0]["total"] if recent_logs else 0,
                "error_logs_1h": recent_logs[0]["errors"] if recent_logs and recent_logs[0]["errors"] else 0,
                "active_alerts": active_alerts[0]["cnt"] if active_alerts else 0,
                "status": "healthy" if error_rate < 5 else "degraded" if error_rate < 20 else "unhealthy",
            }

        return health

    async def get_ai_observability(
        self,
        model: Optional[str] = None,
        start_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get AI-specific observability data.

        Correlates with Langfuse and Opik for AI model tracing.
        """
        # Get Shrewd-related traces (LLM calls)
        query = "SELECT * FROM traces WHERE operation LIKE '%chat%' OR operation LIKE '%completion%' OR operation LIKE '%embedding%'"
        params: List[Any] = []

        if model:
            query += " AND tags LIKE ?"
            params.append(f"%\"{model}\"%")
        if start_time:
            query += " AND created_at >= ?"
            params.append(start_time)

        query += " ORDER BY start_time DESC LIMIT 100"
        ai_traces = await self.db.fetchall(query, params)

        # Get Shrewd usage metrics
        usage_metrics = await self.db.fetchall(
            "SELECT * FROM metrics WHERE name LIKE '%token%' OR name LIKE '%latency%' OR name LIKE '%cost%' ORDER BY timestamp DESC LIMIT 50"
        )

        # Get Langfuse status
        langfuse_status = await self._check_langfuse_status()

        # Get Opik status
        opik_status = await self._check_opik_status()

        return {
            "ai_traces": ai_traces,
            "usage_metrics": usage_metrics,
            "trace_count": len(ai_traces),
            "integrations": {
                "langfuse": langfuse_status,
                "opik": opik_status,
            },
        }

    async def _check_langfuse_status(self) -> Dict[str, Any]:
        """Check if Langfuse is available."""
        langfuse_url = "http://langfuse:3000"
        try:
            response = await self.http_client.get(f"{langfuse_url}/api/public/health", timeout=2)
            return {
                "available": response.status_code == 200,
                "url": langfuse_url,
            }
        except Exception:
            return {
                "available": False,
                "url": langfuse_url,
                "error": "Langfuse not reachable",
            }

    async def _check_opik_status(self) -> Dict[str, Any]:
        """Check if Opik is available."""
        opik_url = "http://opik:8080"
        try:
            response = await self.http_client.get(f"{opik_url}/health", timeout=2)
            return {
                "available": response.status_code == 200,
                "url": opik_url,
            }
        except Exception:
            return {
                "available": False,
                "url": opik_url,
                "error": "Opik not reachable",
            }

    async def get_loki_logs(
        self,
        query: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Query Loki for log aggregation.

        This is a proxy to Loki's API for centralized log querying.
        """
        loki_url = "http://loki:3100"
        try:
            # Build Loki query
            loki_query = f'{{service_name="{query}"}}' if query else "{__name__=~\".*\"}"

            params = {}
            if start_time:
                params["start"] = start_time
            if end_time:
                params["end"] = end_time
            params["limit"] = str(limit)

            response = await self.http_client.get(
                f"{loki_url}/loki/api/v1/query_range",
                params={**params, "query": loki_query},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "loki",
                    "data": data,
                    "available": True,
                }
        except Exception as ex:
            logger.warning(f"Loki query failed: {ex}")
            return {
                "source": "loki",
                "data": [],
                "available": False,
                "error": str(ex),
            }

        return {
            "source": "loki",
            "data": [],
            "available": False,
            "error": "Loki not reachable",
        }

    async def get_tempo_traces(
        self,
        service_name: Optional[str] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Query Tempo for distributed traces.

        This is a proxy to Tempo's API for trace searching.
        """
        tempo_url = "http://tempo:3200"
        try:
            params: Dict[str, str] = {"limit": str(limit)}
            if service_name:
                params["service"] = service_name

            response = await self.http_client.get(
                f"{tempo_url}/api/search",
                params=params,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "tempo",
                    "data": data,
                    "available": True,
                }
        except Exception as ex:
            logger.warning(f"Tempo query failed: {ex}")
            return {
                "source": "tempo",
                "data": [],
                "available": False,
                "error": str(ex),
            }

        return {
            "source": "tempo",
            "data": [],
            "available": False,
            "error": "Tempo not reachable",
        }

    async def get_dashboard_data(
        self,
    ) -> Dict[str, Any]:
        """Get aggregated data for Grafana dashboards."""
        # Service health
        health = await self.get_service_health()

        # Recent alerts
        alerts = await self.db.fetchall(
            """SELECT ah.*, ar.name as rule_name, ar.severity
            FROM alert_history ah
            JOIN alert_rules ar ON ah.rule_id = ar.id
            ORDER BY ah.triggered_at DESC LIMIT 10"""
        )

        # Top services by trace count
        top_services = await self.db.fetchall(
            """SELECT service_name, COUNT(*) as trace_count
            FROM traces
            WHERE created_at >= datetime('now', '-1 hour')
            GROUP BY service_name
            ORDER BY trace_count DESC
            LIMIT 10"""
        )

        # Error rate trend
        error_trend = await self.db.fetchall(
            """SELECT
                strftime('%Y-%m-%dT%H:00:00', created_at) as hour,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'ERROR' THEN 1 ELSE 0 END) as errors
            FROM traces
            WHERE created_at >= datetime('now', '-24 hours')
            GROUP BY hour
            ORDER BY hour"""
        )

        return {
            "service_health": health,
            "recent_alerts": alerts,
            "top_services": top_services,
            "error_trend": error_trend,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
