"""Shrewd — Chat completions and provider delegation routes."""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter

from evershade.errors import EvershadeError

from app.database import db
from app.models import ChatCompletionCreate, ChatCompletionResponse

# Langfuse integration (optional)
langfuse_client = None
try:
    from langfuse import get_langfuse_client
    langfuse_client = get_langfuse_client()
except ImportError:
    pass

router = APIRouter(prefix="/api", tags=["chat"])


async def _resolve_model(model_name: str) -> dict[str, Any] | None:
    """Resolve a model name to its database record."""
    row = await db.fetchone(
        "SELECT m.*, p.base_url, p.api_key, p.enabled as provider_enabled FROM models m JOIN providers p ON m.provider_id = p.id WHERE m.name = ? AND m.enabled = 1",
        [model_name],
    )
    if not row:
        return None
    return row


async def _record_usage(
    model_id: str, provider_id: str, input_tokens: int, output_tokens: int,
    duration_ms: int, status: str, error_message: str = "", user_id: str = "",
    request_id: str = "",
) -> None:
    """Record a usage entry."""
    usage_id = str(uuid.uuid4())
    total_tokens = input_tokens + output_tokens
    now = datetime.now(timezone.utc).isoformat()
    row = await db.fetchone("SELECT input_cost_per_token, output_cost_per_token FROM models WHERE id = ?", [model_id])
    cost = 0.0
    if row:
        cost = (input_tokens * (row["input_cost_per_token"] or 0.0) +
                output_tokens * (row["output_cost_per_token"] or 0.0))
    await db.execute(
        """INSERT INTO usage (id, model_id, provider_id, input_tokens, output_tokens,
           total_tokens, estimated_cost, duration_ms, status, error_message, user_id, request_id, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [usage_id, model_id, provider_id, input_tokens, output_tokens,
         total_tokens, cost, duration_ms, status, error_message[:500],
         user_id, request_id, now],
    )


@router.post("/chat/completions")
async def chat_completions(data: ChatCompletionCreate):
    """Process a chat completion request, delegating to the appropriate provider."""
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Langfuse trace
    lf_trace_id = None
    if langfuse_client and langfuse_client.enabled:
        from langfuse import LangfuseTrace
        trace = LangfuseTrace(
            name="shrewd.chat.completion",
            input={"model": data.model, "messages": [m.model_dump() for m in data.messages]},
            user_id=data.user_id or None,
            metadata={"request_id": request_id},
        )
        lf_trace_id = langfuse_client.create_trace(trace)

    # Resolve model
    model_info = await _resolve_model(data.model)
    if not model_info:
        raise EvershadeError.not_found(f"Model not found: {data.model}")

    if not model_info["provider_enabled"]:
        raise EvershadeError.service_unavailable(f"Provider '{model_info['name']}' is disabled")

    provider_url = model_info["base_url"].rstrip("/")
    api_key = model_info["api_key"]

    if not provider_url:
        raise EvershadeError.internal_error(f"Provider '{model_info['name']}' has no base_url configured")

    # Build the request payload
    messages = [{"role": m.role, "content": m.content} for m in data.messages]
    payload: dict[str, Any] = {
        "model": data.model,
        "messages": messages,
        "temperature": data.temperature,
        "top_p": data.top_p,
    }
    if data.max_tokens:
        payload["max_tokens"] = data.max_tokens

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{provider_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            )

        duration_ms = int((time.time() - start_time) * 1000)

        if resp.status_code >= 400:
            await _record_usage(
                model_info["id"], model_info["provider_id"], 0, 0,
                duration_ms, "error", resp.text[:500], data.user_id, request_id,
            )
            # Langfuse error span
            if lf_trace_id and langfuse_client:
                span = langfuse_client.create_span(lf_trace_id, "provider_call", input_data={"status": resp.status_code})
                langfuse_client.end_span(span, error=resp.text[:500])
            raise EvershadeError.bad_gateway(resp.text)

        result = resp.json()

        # Extract token usage
        usage = result.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = input_tokens + output_tokens

        await _record_usage(
            model_info["id"], model_info["provider_id"],
            input_tokens, output_tokens, duration_ms, "success",
            "", data.user_id, request_id,
        )

        # Langfuse generation logging
        if lf_trace_id and langfuse_client:
            output_content = ""
            if "choices" in result and result["choices"]:
                output_content = result["choices"][0].get("message", {}).get("content", "")
            langfuse_client.log_generation(
                trace_id=lf_trace_id,
                name="provider_call",
                model=data.model,
                input_messages=messages,
                output=output_content,
                tokens=total_tokens,
            )

        # Add request_id to response
        result["request_id"] = request_id
        return result

    except httpx.TimeoutException:
        duration_ms = int((time.time() - start_time) * 1000)
        await _record_usage(
            model_info["id"], model_info["provider_id"], 0, 0,
            duration_ms, "timeout", "Request timed out", data.user_id, request_id,
        )
        if lf_trace_id and langfuse_client:
            span = langfuse_client.create_span(lf_trace_id, "provider_call", input_data={"error": "timeout"})
            langfuse_client.end_span(span, error="Request timed out")
        raise EvershadeError.gateway_timeout("Provider request timed out")
    except EvershadeError:
        raise
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        await _record_usage(
            model_info["id"], model_info["provider_id"], 0, 0,
            duration_ms, "error", str(e)[:500], data.user_id, request_id,
        )
        if lf_trace_id and langfuse_client:
            span = langfuse_client.create_span(lf_trace_id, "provider_call", input_data={"error": str(e)[:200]})
            langfuse_client.end_span(span, error=str(e)[:500])
        raise EvershadeError.bad_gateway(f"Provider error: {str(e)}")


@router.get("/chat/models")
async def list_available_models():
    """List all available models for chat completions (OpenAI-compatible)."""
    rows = await db.fetchall(
        """SELECT m.id, m.name, m.context_window, m.max_tokens, m.supports_vision,
           m.supports_tools, p.name as provider_name
           FROM models m JOIN providers p ON m.provider_id = p.id
           WHERE m.enabled = 1 AND p.enabled = 1
           ORDER BY p.name, m.name"""
    )
    models = []
    for r in rows:
        models.append({
            "id": r["id"],
            "name": r["name"],
            "provider": r["provider_name"],
            "context_window": r["context_window"],
            "max_tokens": r["max_tokens"],
            "supports_vision": bool(r["supports_vision"]),
            "supports_tools": bool(r["supports_tools"]),
        })
    return {"models": models, "count": len(models)}
