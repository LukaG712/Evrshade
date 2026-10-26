"""Shrewd — Model routing with fallback policies, retries, and Hider integration.

Provides configurable routing rules, fallback chains, per-task model selection,
timeout handling, and credential retrieval from Hider service.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from evershade.errors import EvershadeError

from app.database import db


@dataclass
class RoutingRule:
    """A routing rule that determines which model to use."""
    id: str
    name: str
    description: str = ""
    # Conditions
    task_type: str = ""  # e.g., "coding", "chat", "analysis"
    min_capability: str = ""  # e.g., "vision", "tools"
    max_cost: float = 0.0  # 0 = unlimited
    # Model selection
    model_name: str = ""
    fallback_models: list[str] = field(default_factory=list)
    # Retry policy
    max_retries: int = 2
    timeout_seconds: float = 120.0
    # Metadata
    enabled: bool = True
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelRouter:
    """
    Model routing engine with fallback policies and retry logic.

    Features:
    - Configurable routing rules based on task type, capabilities, cost
    - Fallback chains when primary model fails
    - Retry with exponential backoff
    - Per-task model selection
    - Hider credential integration
    - Usage tracking
    """

    def __init__(self, hider_url: str = ""):
        self.hider_url = hider_url.rstrip("/")
        self._rules: dict[str, RoutingRule] = {}
        self._load_rules()

    async def _load_rules(self):
        """Load routing rules from database."""
        rows = await db.fetchall(
            "SELECT * FROM routing_rules WHERE enabled = 1 ORDER BY priority DESC"
        )
        for row in rows:
            rule = RoutingRule(
                id=row["id"],
                name=row["name"],
                description=row.get("description", ""),
                task_type=row.get("task_type", ""),
                min_capability=row.get("min_capability", ""),
                max_cost=float(row.get("max_cost", 0) or 0),
                model_name=row.get("model_name", ""),
                fallback_models=json.loads(row.get("fallback_models", "[]")),
                max_retries=int(row.get("max_retries", 2) or 2),
                timeout_seconds=float(row.get("timeout_seconds", 120) or 120),
                enabled=bool(row.get("enabled", True)),
                priority=int(row.get("priority", 0) or 0),
                metadata=json.loads(row.get("metadata", "{}")),
            )
            self._rules[rule.id] = rule

    def get_rules(self) -> list[RoutingRule]:
        """Get all routing rules."""
        return list(self._rules.values())

    def get_rule(self, rule_id: str) -> Optional[RoutingRule]:
        """Get a specific routing rule."""
        return self._rules.get(rule_id)

    async def add_rule(self, rule_data: dict[str, Any]) -> RoutingRule:
        """Add a new routing rule."""
        rule_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        rule = RoutingRule(
            id=rule_id,
            name=rule_data.get("name", ""),
            description=rule_data.get("description", ""),
            task_type=rule_data.get("task_type", ""),
            min_capability=rule_data.get("min_capability", ""),
            max_cost=float(rule_data.get("max_cost", 0) or 0),
            model_name=rule_data.get("model_name", ""),
            fallback_models=rule_data.get("fallback_models", []),
            max_retries=int(rule_data.get("max_retries", 2) or 2),
            timeout_seconds=float(rule_data.get("timeout_seconds", 120) or 120),
            enabled=bool(rule_data.get("enabled", True)),
            priority=int(rule_data.get("priority", 0) or 0),
            metadata=rule_data.get("metadata", {}),
        )

        await db.execute(
            """INSERT INTO routing_rules (id, name, description, task_type, min_capability,
               max_cost, model_name, fallback_models, max_retries, timeout_seconds,
               enabled, priority, metadata, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                rule_id, rule.name, rule.description, rule.task_type,
                rule.min_capability, rule.max_cost, rule.model_name,
                json.dumps(rule.fallback_models), rule.max_retries,
                rule.timeout_seconds, 1 if rule.enabled else 0,
                rule.priority, json.dumps(rule.metadata), now, now,
            ],
        )

        self._rules[rule_id] = rule
        return rule

    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a routing rule."""
        if rule_id not in self._rules:
            return False
        await db.execute("DELETE FROM routing_rules WHERE id = ?", [rule_id])
        del self._rules[rule_id]
        return True

    def match_rule(
        self,
        task_type: str = "",
        required_capability: str = "",
        max_cost: float = 0.0,
    ) -> Optional[RoutingRule]:
        """Find the best matching routing rule."""
        candidates = []

        for rule in self._rules.values():
            if not rule.enabled:
                continue

            # Check task type
            if rule.task_type and rule.task_type != task_type:
                continue

            # Check capability
            if rule.min_capability and rule.min_capability != required_capability:
                continue

            # Check cost
            if rule.max_cost > 0 and max_cost > 0 and max_cost < rule.max_cost:
                continue

            candidates.append(rule)

        if not candidates:
            return None

        # Return highest priority rule
        candidates.sort(key=lambda r: r.priority, reverse=True)
        return candidates[0]

    async def resolve_model(
        self,
        model_name: str = "",
        task_type: str = "",
        required_capability: str = "",
        max_cost: float = 0.0,
    ) -> dict[str, Any] | None:
        """
        Resolve the best model for a task.

        First tries to find a matching routing rule, then falls back to
        direct model lookup.
        """
        # Try routing rule first
        rule = self.match_rule(task_type, required_capability, max_cost)
        if rule and rule.model_name:
            model_name = rule.model_name

        if not model_name:
            return None

        # Look up model in database
        model_info = await self._lookup_model(model_name)
        if model_info:
            return model_info

        return None

    async def _lookup_model(self, model_name: str) -> dict[str, Any] | None:
        """Look up a model by name."""
        row = await db.fetchone(
            """SELECT m.*, p.name as provider_name, p.base_url, p.api_key,
                      p.enabled as provider_enabled
               FROM models m
               JOIN providers p ON m.provider_id = p.id
               WHERE m.name = ? AND m.enabled = 1""",
            [model_name],
        )
        if not row:
            return None
        return dict(row)

    async def call_with_fallback(
        self,
        model_name: str,
        messages: list[dict[str, str]],
        task_type: str = "",
        required_capability: str = "",
        max_cost: float = 0.0,
        user_id: str = "",
        request_id: str = "",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Call a model with fallback chain and retry logic.

        This is the main entry point for model calls with full fallback support.
        """
        if not request_id:
            request_id = str(uuid.uuid4())

        # Resolve model with routing
        model_info = await self.resolve_model(
            model_name, task_type, required_capability, max_cost
        )

        if not model_info:
            # Try direct lookup
            model_info = await self._lookup_model(model_name)

        if not model_info:
            raise EvershadeError.not_found(f"Model not found: {model_name}")

        if not model_info.get("provider_enabled"):
            raise EvershadeError.service_unavailable(
                f"Provider '{model_info['provider_name']}' is disabled"
            )

        # Build fallback chain
        fallback_models = []
        rule = self.match_rule(task_type, required_capability, max_cost)
        if rule:
            fallback_models = rule.fallback_models
            max_retries = rule.max_retries
            timeout = rule.timeout_seconds
        else:
            max_retries = 2
            timeout = 120.0

        # Try primary model, then fallbacks
        models_to_try = [model_info["name"]] + fallback_models
        last_error = None

        for attempt_model in models_to_try:
            model_info = await self._lookup_model(attempt_model)
            if not model_info:
                continue

            # Get credentials from Hider if needed
            api_key = model_info.get("api_key", "")
            if not api_key and self.hider_url:
                try:
                    api_key = await self._get_credential_from_hider(
                        f"provider.{model_info['provider_name']}.api_key"
                    )
                except Exception:
                    pass

            # Try with retries
            for retry in range(max_retries + 1):
                try:
                    result = await self._call_provider(
                        model_info, messages, api_key, timeout,
                        temperature, max_tokens
                    )

                    # Record usage
                    await self._record_usage(
                        model_info["id"], model_info["provider_id"],
                        result.get("usage", {}), "success",
                        user_id, request_id
                    )

                    result["request_id"] = request_id
                    result["model_used"] = attempt_model
                    return result

                except (httpx.TimeoutException, httpx.ConnectError) as e:
                    last_error = str(e)
                    if retry < max_retries:
                        await self._backoff(retry)
                        continue
                    break

                except EvershadeError as e:
                    last_error = str(e)
                    if e.error_code in ("service_unavailable", "gateway_timeout"):
                        if retry < max_retries:
                            await self._backoff(retry)
                            continue
                    break

                except Exception as e:
                    last_error = str(e)
                    break

        # All models and retries failed
        await self._record_usage(
            model_info["id"], model_info["provider_id"],
            {}, "error", user_id, request_id, error_message=last_error or "All models failed"
        )

        raise EvershadeError.service_unavailable(
            f"All models failed: {last_error}"
        )

    async def _call_provider(
        self,
        model_info: dict[str, Any],
        messages: list[dict[str, str]],
        api_key: str,
        timeout: float,
        temperature: float,
        max_tokens: Optional[int],
    ) -> dict[str, Any]:
        """Call a provider's API."""
        provider_url = model_info["base_url"].rstrip("/")
        if not provider_url:
            raise EvershadeError.internal_error("Provider has no base_url configured")

        payload: dict[str, Any] = {
            "model": model_info["name"],
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{provider_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            )

        if resp.status_code >= 400:
            if resp.status_code == 503:
                raise EvershadeError.service_unavailable(resp.text)
            elif resp.status_code == 504:
                raise EvershadeError.gateway_timeout(resp.text)
            else:
                raise EvershadeError.bad_gateway(resp.text)

        return resp.json()

    async def _get_credential_from_hider(self, key: str) -> str:
        """Retrieve a credential from Hider service."""
        if not self.hider_url:
            raise EvershadeError.internal_error("Hider URL not configured")

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{self.hider_url}/api/secrets/{key}",
            )

        if resp.status_code != 200:
            raise EvershadeError.internal_error(f"Failed to get credential from Hider: {resp.status_code}")

        data = resp.json()
        return data.get("value", "")

    async def _record_usage(
        self,
        model_id: str,
        provider_id: str,
        usage: dict[str, int],
        status: str,
        user_id: str = "",
        request_id: str = "",
        error_message: str = "",
        duration_ms: int = 0,
    ):
        """Record usage statistics."""
        usage_id = str(uuid.uuid4())
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = input_tokens + output_tokens
        now = datetime.now(timezone.utc).isoformat()

        # Get cost info
        row = await db.fetchone(
            "SELECT input_cost_per_token, output_cost_per_token FROM models WHERE id = ?",
            [model_id],
        )
        cost = 0.0
        if row:
            cost = (
                input_tokens * (row["input_cost_per_token"] or 0.0)
                + output_tokens * (row["output_cost_per_token"] or 0.0)
            )

        await db.execute(
            """INSERT INTO usage (id, model_id, provider_id, input_tokens, output_tokens,
               total_tokens, estimated_cost, duration_ms, status, error_message,
               user_id, request_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                usage_id, model_id, provider_id,
                input_tokens, output_tokens, total_tokens,
                cost, duration_ms, status,
                (error_message or "")[:500],
                user_id, request_id, now,
            ],
        )

    async def _backoff(self, attempt: int):
        """Exponential backoff between retries."""
        delay = min(2 ** attempt * 0.5, 10.0)
        await asyncio.sleep(delay)

    async def get_usage_stats(
        self,
        model_id: str = "",
        provider_id: str = "",
        start_date: str = "",
        end_date: str = "",
        user_id: str = "",
    ) -> dict[str, Any]:
        """Get usage statistics."""
        query = """SELECT
            m.name as model_name,
            p.name as provider_name,
            COUNT(*) as total_requests,
            SUM(CASE WHEN u.status = 'success' THEN 1 ELSE 0 END) as successful_requests,
            SUM(CASE WHEN u.status = 'error' THEN 1 ELSE 0 END) as failed_requests,
            SUM(u.input_tokens) as total_input_tokens,
            SUM(u.output_tokens) as total_output_tokens,
            SUM(u.total_tokens) as total_tokens,
            SUM(u.estimated_cost) as total_cost,
            AVG(u.duration_ms) as avg_duration_ms,
            MIN(u.duration_ms) as min_duration_ms,
            MAX(u.duration_ms) as max_duration_ms
            FROM usage u
            JOIN models m ON u.model_id = m.id
            JOIN providers p ON u.provider_id = p.id
            WHERE 1=1"""
        params: list[Any] = []

        if model_id:
            query += " AND u.model_id = ?"
            params.append(model_id)
        if provider_id:
            query += " AND u.provider_id = ?"
            params.append(provider_id)
        if start_date:
            query += " AND u.created_at >= ?"
            params.append(start_date)
        if end_date:
            query += " AND u.created_at <= ?"
            params.append(end_date)
        if user_id:
            query += " AND u.user_id = ?"
            params.append(user_id)

        query += " GROUP BY m.name, p.name"

        rows = await db.fetchall(query, params)

        return {
            "stats": [dict(r) for r in rows],
            "count": len(rows),
        }


