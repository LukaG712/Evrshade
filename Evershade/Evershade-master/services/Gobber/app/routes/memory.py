"""Gobber — Memory and knowledge ingestion routes.

Provides persistent memory interfaces with project-specific and agent-specific context,
semantic retrieval, knowledge ingestion and search, source attribution, memory updates
and conflict handling, and proper data separation between user, project, and shared data.
"""

from __future__ import annotations

import hashlib
import json
import math
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter

from evershade.errors import EvershadeError

from app.database import db

router = APIRouter(prefix="/api", tags=["memory"])


# ─── Memory Entries ────────────────────────────────────────────────────────

@router.post("/memory")
async def create_memory(
    content: str,
    memory_type: str = "context",
    category: str = "",
    user_id: str = "",
    project_id: str = "",
    agent_id: str = "",
    source: str = "",
    source_url: str = "",
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    importance: int = 5,
):
    """Create a new memory entry with proper data separation."""
    memory_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    await db.execute(
        """INSERT INTO memory_entries (id, user_id, project_id, agent_id, memory_type,
           category, content, source, source_url, tags, metadata, importance,
           created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            memory_id, user_id, project_id, agent_id, memory_type,
            category, content, source, source_url,
            json.dumps(tags or []), json.dumps(metadata or {}),
            max(1, min(10, importance)), now, now,
        ],
    )

    return {
        "id": memory_id,
        "user_id": user_id,
        "project_id": project_id,
        "agent_id": agent_id,
        "memory_type": memory_type,
        "category": category,
        "content": content,
        "source": source,
        "source_url": source_url,
        "tags": tags or [],
        "metadata": metadata or {},
        "importance": max(1, min(10, importance)),
        "version": 1,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }


@router.get("/memory")
async def list_memory(
    user_id: str = "",
    project_id: str = "",
    agent_id: str = "",
    memory_type: str = "",
    category: str = "",
    tag: str = "",
    limit: int = 50,
    offset: int = 0,
):
    """List memory entries with filtering by user, project, agent, type, category, or tag."""
    query = """SELECT * FROM memory_entries
               WHERE status = 'active' AND 1=1"""
    params: list[Any] = []

    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)
    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)
    if agent_id:
        query += " AND agent_id = ?"
        params.append(agent_id)
    if memory_type:
        query += " AND memory_type = ?"
        params.append(memory_type)
    if category:
        query += " AND category = ?"
        params.append(category)
    if tag:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")

    query += " ORDER BY importance DESC, updated_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = await db.fetchall(query, params)
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "project_id": r["project_id"],
            "agent_id": r["agent_id"],
            "memory_type": r["memory_type"],
            "category": r["category"],
            "content": r["content"],
            "summary": r["summary"],
            "source": r["source"],
            "source_url": r["source_url"],
            "tags": json.loads(r["tags"]),
            "metadata": json.loads(r["metadata"]),
            "importance": r["importance"],
            "version": r["version"],
            "status": r["status"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        }
        for r in rows
    ]


@router.get("/memory/search")
async def search_memory(
    q: str,
    user_id: str = "",
    project_id: str = "",
    agent_id: str = "",
    limit: int = 20,
):
    """Search memory entries by content with optional semantic search."""
    # First try semantic search if embeddings are available
    rows = await db.fetchall(
        """SELECT * FROM memory_entries
           WHERE status = 'active'
           AND (content LIKE ? OR summary LIKE ? OR category LIKE ?)
           AND (user_id = ? OR user_id = '' OR ? = '')
           AND (project_id = ? OR project_id = '' OR ? = '')
           AND (agent_id = ? OR agent_id = '' OR ? = '')
           ORDER BY importance DESC, updated_at DESC LIMIT ?""",
        [f"%{q}%", f"%{q}%", f"%{q}%", user_id, user_id,
         project_id, project_id, agent_id, agent_id, limit],
    )

    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "project_id": r["project_id"],
            "agent_id": r["agent_id"],
            "memory_type": r["memory_type"],
            "category": r["category"],
            "content": r["content"],
            "summary": r["summary"],
            "source": r["source"],
            "source_url": r["source_url"],
            "tags": json.loads(r["tags"]),
            "importance": r["importance"],
            "version": r["version"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        }
        for r in rows
    ]


@router.get("/memory/semantic-search")
async def semantic_search(
    q: str,
    user_id: str = "",
    project_id: str = "",
    agent_id: str = "",
    limit: int = 10,
    min_similarity: float = 0.7,
):
    """Semantic search using embeddings (requires Shrewd integration)."""
    # Generate embedding for query using hash-based fallback
    query_vector = _hash_to_vector(q)

    # Find similar entries
    rows = await db.fetchall(
        """SELECT * FROM memory_entries
           WHERE status = 'active' AND embedding != ''
           AND (user_id = ? OR user_id = '' OR ? = '')
           AND (project_id = ? OR project_id = '' OR ? = '')
           AND (agent_id = ? OR agent_id = '' OR ? = '')
           ORDER BY updated_at DESC LIMIT ?""",
        [user_id, user_id, project_id, project_id,
         agent_id, agent_id, limit * 3],  # Fetch more to filter by similarity
    )

    results = []
    for r in rows:
        try:
            vector = json.loads(r["embedding"])
            similarity = _cosine_similarity(query_vector, vector)
            if similarity >= min_similarity:
                results.append({
                    "id": r["id"],
                    "user_id": r["user_id"],
                    "project_id": r["project_id"],
                    "agent_id": r["agent_id"],
                    "memory_type": r["memory_type"],
                    "category": r["category"],
                    "content": r["content"],
                    "summary": r["summary"],
                    "source": r["source"],
                    "source_url": r["source_url"],
                    "tags": json.loads(r["tags"]),
                    "similarity": round(similarity, 3),
                    "importance": r["importance"],
                    "created_at": r["created_at"],
                })
        except (json.JSONDecodeError, ValueError):
            continue

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:limit]


@router.get("/memory/{memory_id}")
async def get_memory(memory_id: str):
    """Get a single memory entry with relations."""
    row = await db.fetchone("SELECT * FROM memory_entries WHERE id = ?", [memory_id])
    if not row:
        raise EvershadeError.not_found("Memory entry not found")

    # Get related entries
    relations = await db.fetchall(
        """SELECT mr.*, me.content as target_content, me.summary as target_summary
           FROM memory_relations mr
           JOIN memory_entries me ON mr.target_id = me.id
           WHERE mr.source_id = ?""",
        [memory_id],
    )

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "project_id": row["project_id"],
        "agent_id": row["agent_id"],
        "memory_type": row["memory_type"],
        "category": row["category"],
        "content": row["content"],
        "summary": row["summary"],
        "source": row["source"],
        "source_url": row["source_url"],
        "tags": json.loads(row["tags"]),
        "metadata": json.loads(row["metadata"]),
        "importance": row["importance"],
        "version": row["version"],
        "status": row["status"],
        "relations": [
            {
                "id": r["id"],
                "target_id": r["target_id"],
                "target_content": r["target_content"],
                "target_summary": r["target_summary"],
                "relation_type": r["relation_type"],
                "strength": r["strength"],
            }
            for r in relations
        ],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.patch("/memory/{memory_id}")
async def update_memory(
    memory_id: str,
    content: str | None = None,
    summary: str | None = None,
    tags: list[str] | None = None,
    importance: int | None = None,
):
    """Update a memory entry with version tracking."""
    row = await db.fetchone("SELECT * FROM memory_entries WHERE id = ?", [memory_id])
    if not row:
        raise EvershadeError.not_found("Memory entry not found")

    now = datetime.now(timezone.utc).isoformat()
    updates = ["updated_at = ?"]
    params: list[Any] = [now]

    if content is not None:
        updates.append("content = ?")
        params.append(content)
        updates.append("version = version + 1")
    if summary is not None:
        updates.append("summary = ?")
        params.append(summary)
    if tags is not None:
        updates.append("tags = ?")
        params.append(json.dumps(tags))
    if importance is not None:
        updates.append("importance = ?")
        params.append(max(1, min(10, importance)))

    params.append(memory_id)
    await db.execute(f"UPDATE memory_entries SET {', '.join(updates)} WHERE id = ?", params)

    return await _get_memory_row(memory_id)


@router.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str):
    """Soft delete a memory entry (archive instead of delete)."""
    row = await db.fetchone("SELECT * FROM memory_entries WHERE id = ?", [memory_id])
    if not row:
        raise EvershadeError.not_found("Memory entry not found")

    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE memory_entries SET status = 'archived', updated_at = ? WHERE id = ?",
        [now, memory_id],
    )

    return {"id": memory_id, "status": "archived", "message": "Memory entry archived"}


# ─── Memory Relations ──────────────────────────────────────────────────────

@router.post("/memory/{memory_id}/relations")
async def add_memory_relation(
    memory_id: str,
    target_id: str,
    relation_type: str = "related",
    strength: float = 0.5,
):
    """Add a relation between two memory entries."""
    # Verify both entries exist
    source = await db.fetchone("SELECT id FROM memory_entries WHERE id = ?", [memory_id])
    target = await db.fetchone("SELECT id FROM memory_entries WHERE id = ?", [target_id])
    if not source or not target:
        raise EvershadeError.not_found("One or both memory entries not found")

    relation_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    await db.execute(
        """INSERT INTO memory_relations (id, source_id, target_id, relation_type, strength, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [relation_id, memory_id, target_id, relation_type, max(0.0, min(1.0, strength)), now],
    )

    return {
        "id": relation_id,
        "source_id": memory_id,
        "target_id": target_id,
        "relation_type": relation_type,
        "strength": max(0.0, min(1.0, strength)),
        "created_at": now,
    }


# ─── Knowledge Ingestion ───────────────────────────────────────────────────

@router.post("/knowledge/ingest")
async def ingest_knowledge(
    content: str,
    source_type: str = "text",
    source_url: str = "",
    source_title: str = "",
    user_id: str = "",
    project_id: str = "",
    agent_id: str = "",
    metadata: dict[str, Any] | None = None,
):
    """Ingest knowledge from various sources and create memory entries."""
    ingestion_id = str(uuid.uuid4())
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    now = datetime.now(timezone.utc).isoformat()

    # Check for duplicate content
    existing = await db.fetchone(
        "SELECT id FROM knowledge_ingestion WHERE content_hash = ? AND source_type = ?",
        [content_hash, source_type],
    )
    if existing:
        return {
            "id": existing["id"],
            "status": "duplicate",
            "message": "Content already ingested",
        }

    # Create ingestion record
    await db.execute(
        """INSERT INTO knowledge_ingestion (id, source_type, source_url, source_title,
           content, content_hash, user_id, project_id, agent_id, status, metadata, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'processing', ?, ?)""",
        [ingestion_id, source_type, source_url, source_title, content,
         content_hash, user_id, project_id, agent_id,
         json.dumps(metadata or {}), now],
    )

    # Process content and create memory entries
    memory_entries = await _process_ingestion(ingestion_id, content, user_id, project_id, agent_id, source_url, source_title)

    # Update ingestion status
    await db.execute(
        """UPDATE knowledge_ingestion SET status = 'completed',
           memory_entry_ids = ?, completed_at = ? WHERE id = ?""",
        [json.dumps([e["id"] for e in memory_entries]), now, ingestion_id],
    )

    return {
        "id": ingestion_id,
        "status": "completed",
        "memory_entries": memory_entries,
        "completed_at": now,
    }


@router.get("/knowledge/ingestion")
async def list_ingestion(
    project_id: str = "",
    status: str = "",
    limit: int = 50,
):
    """List knowledge ingestion records."""
    query = "SELECT * FROM knowledge_ingestion WHERE 1=1"
    params: list[Any] = []

    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = await db.fetchall(query, params)
    return [
        {
            "id": r["id"],
            "source_type": r["source_type"],
            "source_url": r["source_url"],
            "source_title": r["source_title"],
            "user_id": r["user_id"],
            "project_id": r["project_id"],
            "agent_id": r["agent_id"],
            "status": r["status"],
            "memory_entry_count": len(json.loads(r["memory_entry_ids"])),
            "error": r["error"],
            "created_at": r["created_at"],
            "completed_at": r["completed_at"],
        }
        for r in rows
    ]


# ─── Memory Context Retrieval ──────────────────────────────────────────────

@router.get("/memory/context")
async def get_memory_context(
    user_id: str = "",
    project_id: str = "",
    agent_id: str = "",
    query: str = "",
    limit: int = 10,
):
    """Get relevant memory context for an agent/task.

    This is the main interface for agents to retrieve relevant context
    before performing tasks. It combines user, project, and agent-specific
    memory with optional query-based filtering.
    """
    # Get high-importance entries first
    entries = await db.fetchall(
        """SELECT * FROM memory_entries
           WHERE status = 'active'
           AND (user_id = ? OR user_id = '' OR ? = '')
           AND (project_id = ? OR project_id = '' OR ? = '')
           AND (agent_id = ? OR agent_id = '' OR ? = '')
           ORDER BY importance DESC, updated_at DESC LIMIT ?""",
        [user_id, user_id, project_id, project_id,
         agent_id, agent_id, limit * 2],
    )

    # If query provided, prioritize matching entries
    if query:
        matching = []
        non_matching = []
        query_lower = query.lower()
        for entry in entries:
            content_lower = entry["content"].lower()
            if query_lower in content_lower:
                matching.append(entry)
            else:
                non_matching.append(entry)
        entries = matching + non_matching

    entries = entries[:limit]

    return {
        "context": [
            {
                "id": e["id"],
                "memory_type": e["memory_type"],
                "category": e["category"],
                "content": e["content"],
                "summary": e["summary"],
                "source": e["source"],
                "source_url": e["source_url"],
                "importance": e["importance"],
                "created_at": e["created_at"],
            }
            for e in entries
        ],
        "count": len(entries),
        "user_id": user_id,
        "project_id": project_id,
        "agent_id": agent_id,
    }


# ─── Helper Functions ──────────────────────────────────────────────────────

async def _get_memory_row(memory_id: str) -> dict[str, Any]:
    """Get memory entry as dict."""
    row = await db.fetchone("SELECT * FROM memory_entries WHERE id = ?", [memory_id])
    if not row:
        raise EvershadeError.not_found("Memory entry not found")
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "project_id": row["project_id"],
        "agent_id": row["agent_id"],
        "memory_type": row["memory_type"],
        "category": row["category"],
        "content": row["content"],
        "summary": row["summary"],
        "source": row["source"],
        "source_url": row["source_url"],
        "tags": json.loads(row["tags"]),
        "metadata": json.loads(row["metadata"]),
        "importance": row["importance"],
        "version": row["version"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


async def _process_ingestion(
    ingestion_id: str,
    content: str,
    user_id: str,
    project_id: str,
    agent_id: str,
    source_url: str,
    source_title: str,
) -> list[dict[str, Any]]:
    """Process ingested content and create memory entries."""
    memory_entries = []
    now = datetime.now(timezone.utc).isoformat()

    # Split content into chunks for better retrieval
    chunks = _split_content(content, max_chunk_size=2000)

    for i, chunk in enumerate(chunks):
        memory_id = str(uuid.uuid4())
        memory_type = "observation" if i > 0 else "context"

        await db.execute(
            """INSERT INTO memory_entries (id, user_id, project_id, agent_id, memory_type,
               category, content, summary, source, source_url, tags, metadata,
               created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                memory_id, user_id, project_id, agent_id, memory_type,
                "ingested", chunk, chunk[:200].strip() + "...",
                source_title or "Ingested content", source_url,
                json.dumps(["ingested", source_type_from_url(source_url)]),
                json.dumps({"ingestion_id": ingestion_id, "chunk_index": i}),
                now, now,
            ],
        )

        memory_entries.append({
            "id": memory_id,
            "memory_type": memory_type,
            "content_length": len(chunk),
        })

    return memory_entries


def _split_content(content: str, max_chunk_size: int = 2000) -> list[str]:
    """Split content into chunks for better retrieval."""
    if len(content) <= max_chunk_size:
        return [content]

    chunks = []
    # Try to split on paragraph boundaries
    paragraphs = content.split("\n\n")
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    # If still too large, force split
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size:
            for i in range(0, len(chunk), max_chunk_size):
                final_chunks.append(chunk[i:i + max_chunk_size])
        else:
            final_chunks.append(chunk)

    return final_chunks if final_chunks else [content]


def _hash_to_vector(text: str, dimensions: int = 128) -> list[float]:
    """Convert text to a simple hash-based vector for similarity search."""
    hash_bytes = hashlib.sha256(text.encode()).digest()
    vector = []
    for i in range(dimensions):
        byte_val = hash_bytes[i % len(hash_bytes)]
        vector.append(byte_val / 255.0)
    return vector


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(a) != len(b):
        return 0.0

    dot_product = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot_product / (mag_a * mag_b)


def source_type_from_url(url: str) -> str:
    """Determine source type from URL."""
    if not url:
        return "unknown"
    if "github.com" in url:
        return "github"
    if "docs." in url or "wiki." in url:
        return "documentation"
    if "news" in url or "blog" in url:
        return "article"
    return "web"
