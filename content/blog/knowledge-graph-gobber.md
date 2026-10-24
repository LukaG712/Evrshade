---
title: 'The Knowledge Graph: How Gobber Remembers Everything'
date: '2024-11-22'
slug: 'knowledge-graph-gobber'
excerpt: 'An explanation of the knowledge graph memory system that powers persistent context across AI agent sessions.'
---

Most AI coding tools have amnesia. Once a session ends, all context is lost. Gobber, Evershade's knowledge graph service, changes that.

## The problem

AI agents need context to be effective. They need to know:

- What code was written in previous sessions
- What decisions were made and why
- What APIs are available and how they work
- What the project structure looks like

Without persistent memory, every session starts from scratch.

## Three layers of memory

Gobber combines three approaches to give agents rich, persistent context:

### 1. Keyword search

Traditional full-text search over code, documentation, and conversation history. Fast and precise for exact matches.

### 2. Vector embeddings

Semantic search using embeddings. Ask "how do I authenticate users?" and Gobber finds relevant code even if it doesn't contain those exact words.

### 3. Graph relationships

Entities (files, functions, APIs, decisions) are connected by relationships. "This function calls that API" or "This decision was made because of that constraint."

## How it works in practice

When a mission runs:

1. Greenie queries Gobber for relevant context before planning
2. As features are executed, new knowledge is stored
3. After the mission, the knowledge graph is updated with what was learned

Next time a similar mission runs, the agent starts with all the context from before.

## Storage

Gobber uses SQLite with FTS5 for full-text search and a custom vector index for embeddings. The graph is stored as adjacency lists — simple, fast, and queryable with SQL.

## Privacy

All knowledge stays on your machine. Gobber never sends data to external services. Your code, your decisions, your memory.

## Conclusion

The knowledge graph is what makes Evershade's agents genuinely intelligent over time. They don't just execute tasks — they learn from them.
