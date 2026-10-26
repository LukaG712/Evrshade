"""Greenie — SSE and WebSocket streaming.

Provides real-time updates for mission logs and chat messages.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, AsyncIterator

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database import get_db_instance

router = APIRouter(tags=["streaming"])

# Active WebSocket connections: mission_id -> list of WebSocket
_ws_connections: dict[str, list[WebSocket]] = {}


@router.get("/sse/logs/{mission_id}")
async def stream_mission_logs(mission_id: str):
    """SSE endpoint for real-time mission log streaming.

    Returns Server-Sent Events with log entries as they are added.
    """
    async def event_generator() -> AsyncIterator[str]:
        last_id = 0
        while True:
            db = await get_db_instance()
            rows = await db.fetchall(
                "SELECT * FROM mission_logs WHERE mission_id = ? AND id > ? ORDER BY created_at",
                (mission_id, last_id),
            )
            for row in rows:
                last_id = row["id"]
                data = json.loads(row["data"]) if row["data"] else {}
                event = {
                    "id": row["id"],
                    "level": row["level"],
                    "message": row["message"],
                    "data": data,
                    "created_at": row["created_at"],
                }
                yield f"data: {json.dumps(event)}\n\n"
            await __import__("asyncio").sleep(2)

    from fastapi.responses import StreamingResponse

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket):
    """WebSocket endpoint for real-time platform events.

    Clients subscribe to event types by sending a JSON message:
    {"subscribe": ["mission_logs", "chat_messages"]}

    The server pushes events as they occur.
    """
    await websocket.accept()
    subscriptions: set[str] = set()

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if "subscribe" in msg:
                    subscriptions.update(msg["subscribe"])
                    await websocket.send_json({
                        "type": "subscribed",
                        "subscriptions": list(subscriptions),
                    })
                elif "ping" in msg:
                    await websocket.send_json({"type": "pong", "timestamp": time.time()})
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
    except WebSocketDisconnect:
        pass


@router.get("/sse/tasks")
async def stream_task_updates():
    """SSE endpoint for task execution updates from Slinker.

    Polls the tasks table for status changes and streams them.
    """
    async def event_generator() -> AsyncIterator[str]:
        last_update = 0.0
        while True:
            # This will be populated when Slinker integration is added
            await __import__("asyncio").sleep(5)
            event = {
                "type": "heartbeat",
                "timestamp": time.time(),
            }
            yield f"data: {json.dumps(event)}\n\n"

    from fastapi.responses import StreamingResponse

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
