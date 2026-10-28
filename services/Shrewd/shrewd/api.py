"""FastAPI application for Shrewd LLM abstraction service.

Routes chat requests to real LLM providers (OpenAI, Anthropic, Google, Ollama)
with cost tracking and privacy classification.
"""

import hmac
import logging
import os
import time
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from starlette.middleware.cors import CORSMiddleware

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Histogram,
        generate_latest,
    )

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

from shrewd import telemetry as shrewd_telemetry
from shrewd.models import ChatMessage, ChatResponse, Provider
from shrewd.providers import get_provider
from shrewd.routing import (
    MODEL_REGISTRY,
    get_cost_summary,
    resolve_provider,
    route_chat,
)

logger = logging.getLogger("shrewd")

app = FastAPI(
    title="Shrewd",
    description="LLM provider abstraction for the Evershade ecosystem",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Set up OpenTelemetry instrumentation (no-op if SNEAKER_OTLP_ENDPOINT is not set)
shrewd_telemetry.setup_telemetry(app)

_api_key_raw = os.getenv("API_KEY")
if not _api_key_raw:
    raise RuntimeError(
        "API_KEY environment variable is not set. Refusing to start Shrewd without a configured API key."
    )
API_KEY = _api_key_raw


def verify_bearer(authorization: str | None = Header(None)) -> None:
    """Verify Bearer token in Authorization header."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header. Use: Authorization: Bearer <key>",
        )
    if not hmac.compare_digest(token, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "Shrewd"}


# ─── Prometheus Metrics ─────────────────────────────────────────

if HAS_PROMETHEUS:
    shrewd_http_requests_total = Counter(
        "shrewd_http_requests_total",
        "Total HTTP requests to Shrewd",
        ["method", "endpoint", "status"],
    )
    shrewd_http_request_duration = Histogram(
        "shrewd_http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "endpoint"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    )

    @app.middleware("http")
    async def prometheus_middleware(request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        method = request.method
        endpoint = request.url.path
        start = time.time()
        status = "200"
        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception:
            status = "500"
        finally:
            duration = time.time() - start
            shrewd_http_requests_total.labels(
                method=method, endpoint=endpoint, status=status
            ).inc()
            shrewd_http_request_duration.labels(
                method=method, endpoint=endpoint
            ).observe(duration)
        return response

    @app.get("/metrics")
    async def prometheus_metrics(authorization: str | None = Header(None)):
        """Prometheus metrics endpoint for Grafana scraping."""
        verify_bearer(authorization)
        return Response(
            content=generate_latest().decode("utf-8"),
            media_type=CONTENT_TYPE_LATEST,
        )


@app.get("/api/capabilities")
async def capabilities(authorization: str | None = Header(None)) -> dict:
    """Return service identification, version, and features."""
    verify_bearer(authorization)
    return {
        "service": "Shrewd",
        "version": "1.1.0",
        "features": [
            "llm_routing",
            "cost_tracking",
            "privacy_classification",
            "openai",
            "anthropic",
            "google",
            "ollama",
            "prometheus_metrics",
            "opentelemetry",
        ],
    }


@app.post("/api/chat")
async def chat(
    data: dict[str, Any], authorization: str | None = Header(None)
) -> dict[str, Any]:
    """Route a chat request to the appropriate LLM provider.

    Supports real providers: OpenAI, Anthropic, Google Gemini, and Ollama.
    Falls back to simulated response if no provider is configured.
    """
    verify_bearer(authorization)
    model = data.get("model")
    temperature = data.get("temperature", 0.7)
    max_tokens = data.get("max_tokens", 1000)
    require_private = data.get("require_private", False)
    messages_data = data.get("messages", [])

    messages = [
        ChatMessage(role=m["role"], content=m["content"]) for m in messages_data
    ]

    try:
        response = await route_chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            require_private=require_private,
        )
        return response.to_dict()
    except (ValueError, RuntimeError) as e:
        # If provider is not configured, fall back to simulation
        logger.warning(f"Provider error, falling back to simulation: {e}")
        resolved_provider, _ = resolve_provider(model or "llama3")
        # Do NOT echo user input in the response to prevent sensitive data leakage
        response = ChatResponse(
            content=f"[Simulated {resolved_provider.value} response] Provider unavailable. Please check configuration.",
            provider=resolved_provider,
            model=model or "llama3",
            prompt_tokens=0,
            completion_tokens=20,
        )
        return response.to_dict()
    except Exception as e:
        logger.error("Chat error: %s", e)
        raise HTTPException(status_code=502, detail="Provider error")


@app.get("/api/models")
async def list_models(
    provider: str | None = None, authorization: str | None = Header(None)
) -> list[dict[str, Any]]:
    """List available models with provider and privacy info."""
    verify_bearer(authorization)
    results = []
    for name, meta in MODEL_REGISTRY.items():
        prov = meta["provider"]
        if provider and prov.value != provider:
            continue
        prov_instance = get_provider(prov)
        results.append(
            {
                "name": name,
                "provider": prov.value,
                "context_window": meta.get("context_window", 0),
                "is_private": meta.get("is_private", True),
                "is_available": prov_instance.check_available(),
            }
        )
    return results


@app.get("/api/providers")
async def list_providers(
    authorization: str | None = Header(None),
) -> list[dict[str, Any]]:
    """List available providers with availability status."""
    verify_bearer(authorization)
    provider_map = {
        Provider.OPENAI: get_provider(Provider.OPENAI),
        Provider.ANTHROPIC: get_provider(Provider.ANTHROPIC),
        Provider.GOOGLE: get_provider(Provider.GOOGLE),
        Provider.OLLAMA: get_provider(Provider.OLLAMA),
    }
    results = []
    for prov, instance in provider_map.items():
        results.append(
            {
                "name": prov.value,
                "is_available": instance.check_available(),
            }
        )
    return results


@app.get("/api/cost/summary")
async def cost_summary(authorization: str | None = Header(None)) -> dict[str, Any]:
    """Get a summary of tracked LLM usage costs."""
    verify_bearer(authorization)
    return get_cost_summary()
