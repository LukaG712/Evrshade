"""Shared event contracts for Evershade inter-service communication.

Defines typed event classes and a Redis-based event bus for pub/sub
communication between services.

Usage:
    from evershade_events import Event, AgentCreatedEvent, EventBus

    # Create an event
    event = AgentCreatedEvent(agent_id="abc-123", name="My Agent")

    # Publish via event bus
    bus = EventBus(redis_url="redis://localhost:6379")
    await bus.publish(event)

    # Subscribe to events
    async def handler(event: Event):
        print(f"Received: {event.type}")
    await bus.subscribe("agent.*", handler)
"""

from __future__ import annotations

import json
import time
import uuid
from abc import ABC
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Optional

import httpx


class EventType(str, Enum):
    """Standard event types for Evershade."""
    # Agent events
    AGENT_CREATED = "agent.created"
    AGENT_UPDATED = "agent.updated"
    AGENT_DELETED = "agent.deleted"

    # Mission events
    MISSION_STARTED = "mission.started"
    MISSION_COMPLETED = "mission.completed"
    MISSION_FAILED = "mission.failed"
    MISSION_CANCELLED = "mission.cancelled"

    # Task events
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

    # Notification events
    NOTIFICATION_QUEUED = "notification.queued"
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_FAILED = "notification.failed"

    # System events
    SERVICE_REGISTERED = "service.registered"
    SERVICE_DEREGISTERED = "service.deregistered"
    SERVICE_HEALTHY = "service.healthy"
    SERVICE_UNHEALTHY = "service.unhealthy"


@dataclass
class Event:
    """Base event class for all Evershade events.

    Every event contains a standard envelope with metadata and a typed payload.
    """
    type: str
    payload: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    source: str = ""
    correlation_id: str = ""
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "source": self.source,
            "correlationId": self.correlation_id,
            "version": self.version,
            "payload": self.payload,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Event:
        return cls(
            type=data["type"],
            payload=data["payload"],
            id=data.get("id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", time.time()),
            source=data.get("source", ""),
            correlation_id=data.get("correlationId", ""),
            version=data.get("version", "1.0"),
        )

    @classmethod
    def from_json(cls, data: str) -> Event:
        return cls.from_dict(json.loads(data))


@dataclass
class AgentCreatedEvent:
    """Event fired when a new agent is created."""
    agent_id: str
    name: str
    description: str = ""

    def to_event(self, source: str = "Greenie") -> Event:
        return Event(
            type=EventType.AGENT_CREATED.value,
            payload=asdict(self),
            source=source,
        )


@dataclass
class MissionStartedEvent:
    """Event fired when a mission starts."""
    mission_id: str
    agent_id: str
    name: str = ""

    def to_event(self, source: str = "Greenie") -> Event:
        return Event(
            type=EventType.MISSION_STARTED.value,
            payload=asdict(self),
            source=source,
        )


@dataclass
class TaskCompletedEvent:
    """Event fired when a task completes."""
    task_id: str
    worker_id: str = ""
    exit_code: int = 0

    def to_event(self, source: str = "Slinker") -> Event:
        return Event(
            type=EventType.TASK_COMPLETED.value,
            payload=asdict(self),
            source=source,
        )


@dataclass
class NotificationSentEvent:
    """Event fired when a notification is sent."""
    notification_id: str
    channel: str
    recipient: str = ""

    def to_event(self, source: str = "Poltergeist") -> Event:
        return Event(
            type=EventType.NOTIFICATION_SENT.value,
            payload=asdict(self),
            source=source,
        )


# Type alias for event handlers
EventHandler = Callable[[Event], Awaitable[None]]


class EventBus:
    """Event bus for publishing and subscribing to events.

    Supports two backends:
    - In-memory (for development/testing)
    - Redis pub/sub (for production)

    Usage:
        bus = EventBus()  # In-memory
        bus = EventBus(redis_url="redis://localhost:6379")  # Redis
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self._handlers: dict[str, list[EventHandler]] = {}
        self._redis = None

    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to events of a given type.

        Supports wildcard patterns: "agent.*" matches all agent events.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        # Notify in-memory handlers
        for pattern, handlers in self._handlers.items():
            if self._matches(pattern, event.type):
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception:
                        pass  # Don't let one handler break others

        # Publish to Redis if configured
        if self._redis:
            await self._redis.publish(event.type, event.to_json())

    def _matches(self, pattern: str, event_type: str) -> bool:
        """Check if an event type matches a subscription pattern."""
        if pattern == event_type:
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type.startswith(prefix + ".")
        return False


class HttpEventPublisher:
    """Publish events via HTTP to a central event collector.

    Usage:
        publisher = HttpEventPublisher(collector_url="http://Greenie:8080")
        await publisher.publish(event)
    """

    def __init__(self, collector_url: str, timeout: float = 10.0):
        self.collector_url = collector_url.rstrip("/")
        self.timeout = timeout

    async def publish(self, event: Event) -> None:
        """Publish an event via HTTP POST."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                await client.post(
                    f"{self.collector_url}/api/events",
                    content=event.to_json(),
                    headers={"Content-Type": "application/json"},
                )
            except Exception:
                pass  # Don't block the caller on event delivery failures
