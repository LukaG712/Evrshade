"""Tests for evershade_events — Event contracts and bus."""

import pytest
from evershade_events import (
    AgentCreatedEvent,
    Event,
    EventBus,
    EventType,
    MissionStartedEvent,
    TaskCompletedEvent,
)


class TestEvent:
    """Test base Event class."""

    def test_create_event(self):
        event = Event(type="test.event", payload={"key": "value"})
        assert event.type == "test.event"
        assert event.payload == {"key": "value"}
        assert event.version == "1.0"
        assert event.id is not None

    def test_to_dict(self):
        event = Event(type="test.event", payload={"key": "value"})
        d = event.to_dict()
        assert d["type"] == "test.event"
        assert d["payload"] == {"key": "value"}
        assert "timestamp" in d

    def test_to_json(self):
        event = Event(type="test.event", payload={"key": "value"})
        json_str = event.to_json()
        assert "test.event" in json_str

    def test_from_dict(self):
        data = {
            "type": "test.event",
            "payload": {"key": "value"},
            "id": "test-id",
            "timestamp": 1234567890,
            "source": "Greenie",
            "correlationId": "corr-123",
            "version": "1.0",
        }
        event = Event.from_dict(data)
        assert event.type == "test.event"
        assert event.id == "test-id"
        assert event.source == "Greenie"
        assert event.correlation_id == "corr-123"

    def test_from_json(self):
        event = Event(type="test.event", payload={"key": "value"})
        json_str = event.to_json()
        restored = Event.from_json(json_str)
        assert restored.type == event.type
        assert restored.payload == event.payload


class TestTypedEvents:
    """Test typed event classes."""

    def test_agent_created(self):
        event = AgentCreatedEvent(agent_id="abc", name="Test Agent")
        e = event.to_event()
        assert e.type == EventType.AGENT_CREATED.value
        assert e.payload["agent_id"] == "abc"

    def test_mission_started(self):
        event = MissionStartedEvent(mission_id="m1", agent_id="a1")
        e = event.to_event()
        assert e.type == EventType.MISSION_STARTED.value

    def test_task_completed(self):
        event = TaskCompletedEvent(task_id="t1", exit_code=0)
        e = event.to_event()
        assert e.type == EventType.TASK_COMPLETED.value


class TestEventBus:
    """Test event bus pub/sub."""

    @pytest.mark.asyncio
    async def test_publish_and_subscribe(self):
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        await bus.subscribe("test.event", handler)
        event = Event(type="test.event", payload={"key": "value"})
        await bus.publish(event)

        assert len(received) == 1
        assert received[0].type == "test.event"

    @pytest.mark.asyncio
    async def test_wildcard_subscription(self):
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        await bus.subscribe("agent.*", handler)
        await bus.publish(Event(type="agent.created", payload={}))
        await bus.publish(Event(type="agent.updated", payload={}))
        await bus.publish(Event(type="task.created", payload={}))

        assert len(received) == 2

    @pytest.mark.asyncio
    async def test_no_handler(self):
        bus = EventBus()
        # Should not raise
        await bus.publish(Event(type="unknown.event", payload={}))

    @pytest.mark.asyncio
    async def test_handler_exception(self):
        """Handler exception doesn't break other handlers."""
        bus = EventBus()
        received = []

        async def bad_handler(event):
            raise RuntimeError("bad")

        async def good_handler(event):
            received.append(event)

        await bus.subscribe("test.event", bad_handler)
        await bus.subscribe("test.event", good_handler)
        await bus.publish(Event(type="test.event", payload={}))

        assert len(received) == 1


class TestEventType:
    """Test EventType enum."""

    def test_all_types_have_dots(self):
        """All event types use dot notation."""
        for et in EventType:
            assert "." in et.value
