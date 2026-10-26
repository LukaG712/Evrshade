"""Gobber — Knowledge graph routes: notes, embeddings, vault indexing."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import httpx
from fastapi import APIRouter

from evershade.errors import EvershadeError

from app.database import db
from app.models import (
    EmbeddingCreate,
    EmbeddingResponse,
    EmbeddingSearch,
    NoteCreate,
    NoteLinkCreate,
    NoteLinkResponse,
    NoteResponse,
    NoteUpdate,
    VaultFileResponse,
)

router = APIRouter(prefix="/api", tags=["knowledge"])

# Shrewd URL for embedding generation
SHREWD_URL = os.getenv("SHREWD_URL", "")


# ─── Notes ────────────────────────────────────────────────────────────────────

@router.post("/notes", response_model=NoteResponse)
async def create_note(data: NoteCreate):
    note_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """INSERT INTO notes (id, title, content, tags, metadata, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [note_id, data.title, data.content, json.dumps(data.tags),
         json.dumps(data.metadata), now, now],
    )
    return NoteResponse(
        id=note_id, title=data.title, content=data.content,
        tags=data.tags, metadata=data.metadata, created_at=now, updated_at=now,
    )


@router.get("/notes")
async def list_notes(tag: str = "", limit: int = 100):
    if tag:
        rows = await db.fetchall(
            "SELECT * FROM notes WHERE tags LIKE ? ORDER BY updated_at DESC LIMIT ?",
            [f"%{tag}%", limit],
        )
    else:
        rows = await db.fetchall(
            "SELECT * FROM notes ORDER BY updated_at DESC LIMIT ?", [limit]
        )
    return [
        NoteResponse(
            id=r["id"], title=r["title"], content=r["content"],
            tags=json.loads(r["tags"]), metadata=json.loads(r["metadata"]),
            created_at=r["created_at"], updated_at=r["updated_at"],
        )
        for r in rows
    ]


@router.get("/notes/search")
async def search_notes(q: str, limit: int = 20):
    """Simple text search across note titles and content."""
    rows = await db.fetchall(
        """SELECT * FROM notes
           WHERE title LIKE ? OR content LIKE ?
           ORDER BY updated_at DESC LIMIT ?""",
        [f"%{q}%", f"%{q}%", limit],
    )
    return [
        NoteResponse(
            id=r["id"], title=r["title"], content=r["content"],
            tags=json.loads(r["tags"]), metadata=json.loads(r["metadata"]),
            created_at=r["created_at"], updated_at=r["updated_at"],
        )
        for r in rows
    ]


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    row = await db.fetchone("SELECT * FROM notes WHERE id = ?", [note_id])
    if not row:
        raise EvershadeError.not_found("Note not found")
    return NoteResponse(
        id=row["id"], title=row["title"], content=row["content"],
        tags=json.loads(row["tags"]), metadata=json.loads(row["metadata"]),
        created_at=row["created_at"], updated_at=row["updated_at"],
    )


@router.patch("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, data: NoteUpdate):
    now = datetime.now(timezone.utc).isoformat()
    row = await db.fetchone("SELECT * FROM notes WHERE id = ?", [note_id])
    if not row:
        raise EvershadeError.not_found("Note not found")
    updates = ["updated_at = ?"]
    params = [now]
    if data.title is not None:
        updates.append("title = ?"); params.append(data.title)
    if data.content is not None:
        updates.append("content = ?"); params.append(data.content)
    if data.tags is not None:
        updates.append("tags = ?"); params.append(json.dumps(data.tags))
    if data.metadata is not None:
        updates.append("metadata = ?"); params.append(json.dumps(data.metadata))
    params.append(note_id)
    await db.execute(f"UPDATE notes SET {', '.join(updates)} WHERE id = ?", params)
    updated = await db.fetchone("SELECT * FROM notes WHERE id = ?", [note_id])
    return NoteResponse(
        id=updated["id"], title=updated["title"], content=updated["content"],
        tags=json.loads(updated["tags"]), metadata=json.loads(updated["metadata"]),
        created_at=updated["created_at"], updated_at=updated["updated_at"],
    )


@router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    await db.execute("DELETE FROM notes WHERE id = ?", [note_id])
    await db.execute("DELETE FROM note_links WHERE source_id = ? OR target_id = ?", [note_id, note_id])
    return {"deleted": note_id}


# ─── Note Links ───────────────────────────────────────────────────────────────

@router.post("/notes/links", response_model=NoteLinkResponse)
async def create_note_link(data: NoteLinkCreate):
    link_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "INSERT INTO note_links (id, source_id, target_id, relation, created_at) VALUES (?, ?, ?, ?, ?)",
        [link_id, data.source_id, data.target_id, data.relation, now],
    )
    return NoteLinkResponse(
        id=link_id, source_id=data.source_id, target_id=data.target_id,
        relation=data.relation, created_at=now,
    )


@router.get("/notes/{note_id}/links")
async def get_note_links(note_id: str):
    rows = await db.fetchall(
        "SELECT * FROM note_links WHERE source_id = ? OR target_id = ? ORDER BY created_at",
        [note_id, note_id],
    )
    return [
        NoteLinkResponse(
            id=r["id"], source_id=r["source_id"], target_id=r["target_id"],
            relation=r["relation"], created_at=r["created_at"],
        )
        for r in rows
    ]


@router.delete("/notes/links/{link_id}")
async def delete_note_link(link_id: str):
    await db.execute("DELETE FROM note_links WHERE id = ?", [link_id])
    return {"deleted": link_id}


# ─── Embeddings ───────────────────────────────────────────────────────────────

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


async def _generate_embedding(text: str, model: str = "") -> tuple[list[float], str]:
    """Generate an embedding vector via Shrewd or return a simple hash-based fallback."""
    if SHREWD_URL:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{SHREWD_URL}/api/embeddings/generate",
                    json={"texts": [text], "model": model},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if "embeddings" in data and data["embeddings"]:
                        return data["embeddings"][0], data.get("model", model)
        except Exception:
            pass
    # Fallback: simple hash-based vector (not semantically meaningful, but functional)
    h = hashlib.sha256(text.encode()).digest()
    vector = [float(b) / 255.0 for b in h]
    return vector, "hash_fallback"


@router.post("/embeddings/generate")
async def generate_embeddings(data: EmbeddingCreate):
    """Generate embeddings for a list of texts."""
    results = []
    for text in data.texts:
        emb_id = str(uuid.uuid4())
        vector, model = await _generate_embedding(text, data.model)
        now = datetime.now(timezone.utc).isoformat()
        await db.execute(
            """INSERT INTO embeddings (id, text, vector, model, dimensions, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [emb_id, text[:500], json.dumps(vector), model, len(vector),
             json.dumps(data.metadata), now],
        )
        results.append(EmbeddingResponse(
            id=emb_id, text=text[:500], vector=vector, model=model,
            dimensions=len(vector), metadata=data.metadata, created_at=now,
        ))
    return {"embeddings": results, "count": len(results)}


@router.post("/embeddings/search")
async def search_embeddings(data: EmbeddingSearch):
    """Search for similar embeddings using cosine similarity."""
    query_vector, model = await _generate_embedding(data.query, data.model)
    rows = await db.fetchall("SELECT * FROM embeddings ORDER BY created_at DESC LIMIT 1000")
    results = []
    for row in rows:
        try:
            vector = json.loads(row["vector"])
            sim = cosine_similarity(query_vector, vector)
            if sim > 0.1:  # Minimum similarity threshold
                results.append({
                    "id": row["id"],
                    "text": row["text"],
                    "similarity": round(sim, 4),
                    "model": row["model"],
                    "metadata": json.loads(row["metadata"]),
                    "created_at": row["created_at"],
                })
        except (json.JSONDecodeError, ValueError):
            continue
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return {"query": data.query, "results": results[:data.limit], "count": len(results[:data.limit])}


@router.get("/embeddings/stats")
async def embedding_stats():
    """Return embedding statistics."""
    row = await db.fetchone("SELECT COUNT(*) as count, GROUP_CONCAT(DISTINCT model) as models FROM embeddings")
    total = row["count"] if row else 0
    models = row["models"].split(",") if row and row["models"] else []
    return {"total_embeddings": total, "models": models}


# ─── Semantic Search (notes + embeddings) ─────────────────────────────────────

@router.get("/notes/semantic-search")
async def semantic_search_notes(q: str, limit: int = 10):
    """Search notes by semantic similarity using embeddings."""
    query_vector, _ = await _generate_embedding(q)
    rows = await db.fetchall("SELECT * FROM notes WHERE embedding != '' AND embedding IS NOT NULL")
    results = []
    for row in rows:
        try:
            note_vector = json.loads(row["embedding"])
            sim = cosine_similarity(query_vector, note_vector)
            if sim > 0.1:
                results.append({
                    "note": NoteResponse(
                        id=row["id"], title=row["title"], content=row["content"],
                        tags=json.loads(row["tags"]), metadata=json.loads(row["metadata"]),
                        created_at=row["created_at"], updated_at=row["updated_at"],
                    ).model_dump(),
                    "similarity": round(sim, 4),
                })
        except (json.JSONDecodeError, ValueError):
            continue
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return {"query": q, "results": results[:limit], "count": len(results[:limit])}


# ─── Vault Indexing ───────────────────────────────────────────────────────────

VAULT_PATH = os.getenv("GOBBER_VAULT_PATH", "")


@router.post("/vault/sync")
async def sync_vault():
    """Index all markdown files in the Obsidian vault."""
    if not VAULT_PATH:
        raise EvershadeError.bad_request("GOBBER_VAULT_PATH not configured")
    vault_dir = Path(VAULT_PATH)
    if not vault_dir.exists():
        raise EvershadeError.bad_request(f"Vault path does not exist: {VAULT_PATH}")

    synced = 0
    now = datetime.now(timezone.utc).isoformat()

    for md_file in vault_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            rel_path = str(md_file.relative_to(vault_dir))

            # Extract frontmatter tags
            tags = []
            if "---" in content:
                frontmatter = content.split("---")[1]
                for line in frontmatter.split("\n"):
                    if line.strip().startswith("tags:"):
                        tag_str = line.split("tags:")[1].strip()
                        tags = [t.strip().lstrip("#") for t in tag_str.replace("[", "").replace("]", "").split(",") if t.strip()]
                        break

            # Extract wiki links [[...]]
            links = re.findall(r"\[\[([^\]]+)\]\]", content)

            title = md_file.stem

            existing = await db.fetchone("SELECT * FROM vault_files WHERE path = ?", [rel_path])
            if existing and existing["content_hash"] == content_hash:
                continue  # Skip unchanged files
            if existing:
                await db.execute(
                    """UPDATE vault_files SET title = ?, content_hash = ?, tags = ?, links = ?,
                       last_synced = ?, updated_at = ? WHERE path = ?""",
                    [title, content_hash, json.dumps(tags), json.dumps(links), now, now, rel_path],
                )
            else:
                vf_id = str(uuid.uuid4())
                await db.execute(
                    """INSERT INTO vault_files (id, path, title, content_hash, tags, links, last_synced, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    [vf_id, rel_path, title, content_hash, json.dumps(tags), json.dumps(links), now, now, now],
                )
            synced += 1
        except Exception:
            continue

    return {"synced": synced, "vault_path": VAULT_PATH}


@router.get("/vault/files")
async def list_vault_files(tag: str = "", limit: int = 100):
    if tag:
        rows = await db.fetchall(
            "SELECT * FROM vault_files WHERE tags LIKE ? ORDER BY updated_at DESC LIMIT ?",
            [f"%{tag}%", limit],
        )
    else:
        rows = await db.fetchall(
            "SELECT * FROM vault_files ORDER BY updated_at DESC LIMIT ?", [limit]
        )
    return [
        VaultFileResponse(
            id=r["id"], path=r["path"], title=r["title"],
            content_hash=r["content_hash"], tags=json.loads(r["tags"]),
            links=json.loads(r["links"]), embedded=bool(r["embedded"]),
            last_synced=r["last_synced"],
            created_at=r["created_at"], updated_at=r["updated_at"],
        )
        for r in rows
    ]


@router.get("/vault/files/{file_id}")
async def get_vault_file(file_id: str):
    row = await db.fetchone("SELECT * FROM vault_files WHERE id = ?", [file_id])
    if not row:
        raise EvershadeError.not_found("Vault file not found")
    return VaultFileResponse(
        id=row["id"], path=row["path"], title=row["title"],
        content_hash=row["content_hash"], tags=json.loads(row["tags"]),
        links=json.loads(row["links"]), embedded=bool(row["embedded"]),
        last_synced=row["last_synced"],
        created_at=row["created_at"], updated_at=row["updated_at"],
    )


@router.post("/vault/embed-all")
async def embed_vault_files():
    """Generate embeddings for all vault files that don't have them yet."""
    if not VAULT_PATH:
        raise EvershadeError.bad_request("GOBBER_VAULT_PATH not configured")

    embedded = 0
    rows = await db.fetchall("SELECT * FROM vault_files WHERE embedded = 0 LIMIT 100")
    for row in rows:
        try:
            md_file = Path(VAULT_PATH) / row["path"]
            if md_file.exists():
                content = md_file.read_text(encoding="utf-8", errors="replace")
                vector, model = await _generate_embedding(content)
                # Store in notes table with embedding
                note_id = str(uuid.uuid4())
                now = datetime.now(timezone.utc).isoformat()
                await db.execute(
                    """INSERT INTO notes (id, title, content, tags, metadata, embedding, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    [note_id, row["title"], content[:5000], json.loads(row["tags"]),
                     json.dumps({"source": "vault", "path": row["path"]}),
                     json.dumps(vector), now, now],
                )
                await db.execute("UPDATE vault_files SET embedded = 1 WHERE id = ?", [row["id"]])
                embedded += 1
        except Exception:
            continue

    return {"embedded": embedded}
