---
title: "The Knowledge Graph: How Gobber Remembers Everything"
date: "2026-10-12"
slug: "knowledge-graph-gobber"
excerpt: "An explanation of Evershade's knowledge graph memory system, and why it makes your agents smarter over time."
---

Most AI coding tools have amnesia. You close the session, and everything the agent learned — your codebase structure, your preferences, your project conventions — is gone. Next time you start, it's like meeting for the first time.

Evershade's Gobber service solves this problem with a knowledge graph. Here's how it works, and why it matters.

## What is a knowledge graph?

A knowledge graph is a network of entities and relationships. Instead of storing data in rows and columns, you store it as nodes (things) and edges (how they're connected).

For example, in your codebase:

- **Node**: `UserController` (a class)
- **Node**: `authenticate` (a method)
- **Edge**: `authenticate` BELONGS_TO `UserController`
- **Node**: `JWTService` (a class)
- **Edge**: `authenticate` CALLS `JWTService`

This structure mirrors how developers actually think about code. You don't think in tables — you think in relationships.

## How Gobber builds the graph

Gobber doesn't just store static information. It actively learns from your interactions:

### 1. Codebase analysis

When you start a mission, Slinker scans your codebase and sends the structure to Gobber. Gobber creates nodes for every file, class, function, and import — and edges for every relationship between them.

### 2. Mission context

As your agent works, Gobber records what it does. If an agent refactors `UserController.authenticate`, Gobber stores that fact. Next time you ask about authentication, the agent knows what changed and when.

### 3. User preferences

If you consistently prefer certain patterns — like JWT over sessions, or functional over OOP — Gobber learns these preferences and surfaces them in future missions.

### 4. Error patterns

Trapper feeds error data to Gobber. If a certain type of error keeps occurring in a specific module, Gobber flags it. Your agent can then proactively suggest fixes.

## Semantic search

The real power of Gobber comes from semantic search. Instead of keyword matching, Gobber understands the meaning of your queries.

Ask your agent: "How do we handle authentication?"

Gobber doesn't just search for the word "authentication." It searches the knowledge graph for nodes related to authentication, authorization, sessions, tokens, and login — then returns the most relevant context to the agent.

This means your agent can answer questions about your codebase even when the exact keywords don't match. It understands that "user login" and "authentication" are related concepts.

## Persistent memory

Gobber stores everything in SQLite, so your knowledge graph persists across sessions. Close Evershade, restart your machine, come back next week — your agent remembers everything.

This is a game-changer for long-term projects. The more you use Evershade, the smarter your agent becomes. It learns your codebase, your preferences, and your patterns — and uses that knowledge to make better decisions.

## Privacy by design

Your knowledge graph lives on your machine, in a SQLite file. It never leaves your hardware unless you explicitly send it to an API. This is core to Evershade's philosophy: your data stays yours.

## Looking ahead

We're exploring several enhancements for Gobber:

- **Vector embeddings** — Store semantic embeddings alongside the graph for even better search
- **Graph visualization** — A UI to explore the knowledge graph in Slammer
- **Cross-project learning** — Share patterns across projects while keeping data isolated
- **Temporal queries** — "Show me how this module changed over the last month"

The knowledge graph is the foundation of Evershade's intelligence. Without it, agents are just autocomplete on steroids. With it, they're true collaborators that learn and grow with you.

---

*Want to see the knowledge graph in action? Check out our [architecture deep dive](/blog/microservices-architecture) or try Evershade yourself.*
