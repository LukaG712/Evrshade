"""Langfuse integration adapter for Evershade AI observability."""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LangfuseSpan:
    """Represents a Langfuse trace span."""

    trace_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = "span"
    input: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    level: str = "DEFAULT"
    status_message: str | None = None
    parent_observation_id: str | None = None


@dataclass
class LangfuseTrace:
    """Represents a Langfuse trace."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    input: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    user_id: str | None = None
    session_id: str | None = None
    release: str | None = None
    version: str | None = None
    tags: list[str] | None = None
    spans: list[LangfuseSpan] = field(default_factory=list)


class LangfuseClient:
    """Langfuse integration client for AI observability.

    Sends traces and spans to Langfuse for LLM call tracking,
    prompt management, and cost estimation.
    """

    def __init__(
        self,
        endpoint: str | None = None,
        public_key: str | None = None,
        secret_key: str | None = None,
    ):
        self.endpoint = endpoint or os.getenv("LANGFUSE_ENDPOINT")
        self.public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        self.enabled = bool(self.endpoint and self.public_key and self.secret_key)
        self._traces: dict[str, LangfuseTrace] = {}
        self._http_client = None

    def _get_httpx(self):
        """Lazy-load httpx client."""
        if self._http_client is None:
            try:
                import httpx

                self._http_client = httpx.Client(
                    base_url=self.endpoint,
                    headers={
                        "Authorization": f"Basic {__import__('base64').b64encode(f'{self.public_key}:{self.secret_key}'.encode()).decode()}",
                        "Content-Type": "application/json",
                    },
                    timeout=5.0,
                )
            except ImportError:
                self.enabled = False
        return self._http_client

    def create_trace(self, trace: LangfuseTrace) -> str:
        """Create a new trace and return its ID."""
        self._traces[trace.id] = trace
        if self.enabled:
            self._send_batch([trace])
        return trace.id

    def create_span(
        self,
        trace_id: str,
        name: str,
        span_type: str = "span",
        input_data: dict[str, Any] | None = None,
        parent_observation_id: str | None = None,
    ) -> LangfuseSpan:
        """Create a span within a trace."""
        trace = self._traces.get(trace_id)
        if trace is None:
            trace = LangfuseTrace(id=trace_id)
            self._traces[trace_id] = trace

        span = LangfuseSpan(
            trace_id=trace_id,
            name=name,
            type=span_type,
            input=input_data,
            parent_observation_id=parent_observation_id,
        )
        trace.spans.append(span)
        return span

    def end_span(
        self,
        span: LangfuseSpan,
        output: dict[str, Any] | None = None,
        error: str | None = None,
    ):
        """Mark a span as completed."""
        span.end_time = time.time()
        span.output = output
        if error:
            span.level = "ERROR"
            span.status_message = error

    def log_generation(
        self,
        trace_id: str,
        name: str,
        model: str,
        input_messages: Any,
        output: Any,
        tokens: int | None = None,
        cost: float | None = None,
        parent_observation_id: str | None = None,
    ):
        """Log an LLM generation event."""
        span = self.create_span(
            trace_id=trace_id,
            name=name,
            span_type="generation",
            input_data={"messages": input_messages, "model": model},
            parent_observation_id=parent_observation_id,
        )
        metadata = {}
        if tokens:
            metadata["usage"] = {"total_tokens": tokens}
        if cost is not None:
            metadata["cost"] = cost
        if metadata:
            span.metadata = metadata
        span.output = output
        self.end_span(span, output={"content": output})

    def _send_batch(self, traces: list[LangfuseTrace]):
        """Send traces to Langfuse API."""
        if not self.enabled:
            return
        try:
            client = self._get_httpx()
            if client is None:
                return
            # Convert traces to Langfuse batch format
            items = []
            for trace in traces:
                items.append(
                    {
                        "type": "trace",
                        "id": trace.id,
                        "name": trace.name,
                        "input": trace.input,
                        "output": trace.output,
                        "metadata": trace.metadata,
                        "userId": trace.user_id,
                        "sessionId": trace.session_id,
                        "release": trace.release,
                        "version": trace.version,
                        "tags": trace.tags,
                    }
                )
                for span in trace.spans:
                    items.append(
                        {
                            "type": "span",
                            "id": span.id,
                            "traceId": span.trace_id,
                            "name": span.name,
                            "spanType": span.type,
                            "input": span.input,
                            "output": span.output,
                            "metadata": span.metadata,
                            "startTime": span.start_time,
                            "endTime": span.end_time,
                            "level": span.level,
                            "statusMessage": span.status_message,
                            "parentObservationId": span.parent_observation_id,
                        }
                    )
            if items:
                client.post("/api/public/batch", json={"batch": items})
        except Exception:
            # Graceful degradation — don't fail the request
            pass

    def flush(self):
        """Flush all pending traces."""
        if self._traces:
            self._send_batch(list(self._traces.values()))
            self._traces.clear()


# Module-level singleton
_default_client: LangfuseClient | None = None


def get_langfuse_client() -> LangfuseClient:
    """Get or create the default Langfuse client."""
    global _default_client
    if _default_client is None:
        _default_client = LangfuseClient()
    return _default_client
