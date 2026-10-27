"""Slinker — OpenAI-compatible API endpoints.

Provides /v1/chat/completions and /v1/models endpoints for compatibility
with OpenAI SDK clients.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ModelInfo,
)

router = APIRouter(prefix="/v1", tags=["openai"])

# Available models (configured via environment or hardcoded)
AVAILABLE_MODELS = [
    {"id": "gpt-4", "name": "GPT-4"},
    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
    {"id": "slinker-agent", "name": "Slinker Agent"},
]


@router.get("/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    models = []
    for m in AVAILABLE_MODELS:
        models.append(ModelInfo(
            id=m["id"],
            created=int(time.time()),
        ))
    return {"object": "list", "data": models}


@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Chat completions endpoint (OpenAI-compatible).

    This endpoint delegates to the configured LLM provider via Shrewd.
    If Shrewd is not available, it returns a placeholder response.
    """
    import os
    shrewd_url = os.getenv("SHREWD_URL", "")

    if not shrewd_url:
        # Fallback: return a simple response
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        response = ChatCompletionResponse(
            id=completion_id,
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message={"role": "assistant", "content": "Shrewd service is not configured. Set SHREWD_URL to enable LLM routing."},
                    finish_reason="stop",
                )
            ],
        )
        return response

    if request.stream:
        return StreamingResponse(
            _stream_completion(request, shrewd_url),
            media_type="text/event-stream",
        )

    # Non-streaming: delegate to Shrewd
    try:
        import httpx
        from evershade_telemetry import create_traced_httpx_client

        async with create_traced_httpx_client(base_url=shrewd_url, timeout=120.0) as client:
            resp = await client.post("/v1/chat/completions", json=request.model_dump())
            resp.raise_for_status()
            data = resp.json()
            return data
    except Exception as e:
        # Return error as a completion
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        return ChatCompletionResponse(
            id=completion_id,
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message={"role": "assistant", "content": f"Error: {str(e)}"},
                    finish_reason="error",
                )
            ],
        )


async def _stream_completion(request: ChatCompletionRequest, shrewd_url: str) -> AsyncIterator[str]:
    """Stream chat completion response."""
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())

    try:
        import httpx
        from evershade_telemetry import create_traced_httpx_client

        async with create_traced_httpx_client(base_url=shrewd_url, timeout=120.0) as client:
            async with client.stream("POST", "/v1/chat/completions", json=request.model_dump()) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        yield f"{line}\n\n"
    except Exception as e:
        error_data = json.dumps({
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": request.model,
            "choices": [{"index": 0, "delta": {"content": f"Error: {str(e)}"}, "finish_reason": "error"}],
        })
        yield f"data: {error_data}\n\n"
        yield "data: [DONE]\n\n"
