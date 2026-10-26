"""Greenie — Chat session and message routes.

Manages chat sessions and conversation history.
"""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter

from evershade.errors import ErrorCode, EvershadeError

from app.database import get_db_instance
from app.models import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ─── Sessions ────────────────────────────────────────────────────────────────

@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(agent_id: str | None = None):
    """List chat sessions, optionally filtered by agent."""
    db = await get_db_instance()
    if agent_id:
        rows = await db.fetchall(
            "SELECT * FROM chat_sessions WHERE agent_id = ? ORDER BY updated_at DESC",
            (agent_id,),
        )
    else:
        rows = await db.fetchall("SELECT * FROM chat_sessions ORDER BY updated_at DESC")
    return [ChatSessionResponse(**row) for row in rows]


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(session_id: str):
    """Get a single chat session."""
    db = await get_db_instance()
    row = await db.fetchone("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
    if not row:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Session {session_id} not found")
    return ChatSessionResponse(**row)


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_session(session: ChatSessionCreate):
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    db = await get_db_instance()
    await db.execute(
        "INSERT INTO chat_sessions (id, agent_id, user_id, title) VALUES (?, ?, ?, ?)",
        (session_id, session.agent_id, session.user_id, session.title),
    )
    row = await db.fetchone("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
    return ChatSessionResponse(**row)


# ─── Messages ────────────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def list_messages(session_id: str, limit: int = 50, offset: int = 0):
    """List messages in a chat session."""
    db = await get_db_instance()
    session = await db.fetchone("SELECT id FROM chat_sessions WHERE id = ?", (session_id,))
    if not session:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Session {session_id} not found")
    rows = await db.fetchall(
        "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (session_id, limit, offset),
    )
    result = []
    for row in rows:
        row["tool_calls"] = json.loads(row["tool_calls"]) if row["tool_calls"] else []
        result.append(ChatMessageResponse(**row))
    return result


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse, status_code=201)
async def add_message(session_id: str, message: ChatMessageCreate):
    """Add a message to a chat session."""
    if message.session_id != session_id:
        raise EvershadeError(ErrorCode.VALIDATION_ERROR, "Session ID mismatch")

    message_id = str(uuid.uuid4())
    db = await get_db_instance()
    session = await db.fetchone("SELECT id FROM chat_sessions WHERE id = ?", (session_id,))
    if not session:
        raise EvershadeError(ErrorCode.NOT_FOUND, f"Session {session_id} not found")
    await db.execute(
        """INSERT INTO chat_messages (id, session_id, role, content, model, tool_calls, token_count)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            message_id,
            session_id,
            message.role.value,
            message.content,
            message.model,
            json.dumps(message.tool_calls),
            message.token_count,
        ),
    )
    row = await db.fetchone("SELECT * FROM chat_messages WHERE id = ?", (message_id,))
    row["tool_calls"] = json.loads(row["tool_calls"]) if row["tool_calls"] else []
    return ChatMessageResponse(**row)
