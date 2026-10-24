---
title: "Why SQLite-First?"
date: "2026-10-15"
slug: "why-sqlite-first"
excerpt: "Why we chose SQLite as the primary storage layer for an AI agent platform, and why it might be the best decision we've made."
---

When people hear "AI agent platform," they expect PostgreSQL, MongoDB, or at least Redis. Not SQLite.

But after months of prototyping, we landed on SQLite as the primary storage layer for Evershade. Here's why it was the right call, and why it might be the best architectural decision we've made.

## The myth of "SQLite is just for local apps"

SQLite gets dismissed as a "local database" suitable for mobile apps and embedded systems. But the reality is very different:

- **Concurrency** — SQLite handles thousands of reads per second and hundreds of writes per second on a single core.
- **Reliability** — SQLite has ACID compliance that's been battle-tested for decades. It's used by browsers, operating systems, and even some production web services.
- **Simplicity** — No server process, no network overhead, no connection pooling. Just a file.

For a self-hosted platform that runs on a developer's machine, SQLite isn't a compromise — it's the optimal choice.

## Why SQLite fits Evershade

### 1. Zero infrastructure overhead

Evershade runs on Docker Compose. Adding PostgreSQL means another container, another port, another configuration file, and another thing that can break.

With SQLite, every service stores its data in a file mounted from the host. No network calls between your application and your database. No connection timeouts. No "database is unreachable" errors.

### 2. Portability

Your entire Evershade state — missions, knowledge graph, metrics, traces, logs — lives in a single directory of SQLite files. Back it up? Copy the folder. Migrate to a new machine? Copy the folder. Share with a teammate? Copy the folder.

Try doing that with a distributed database cluster.

### 3. Observability

Since SQLite files are just files, you can inspect them with any SQLite browser. No need to learn a query language or spin up an admin panel. Open the file, see the data, done.

This is invaluable for debugging. When an agent behaves unexpectedly, you can directly inspect the knowledge graph, the mission history, and the error logs — all in plain SQL.

### 4. Performance on local hardware

SQLite doesn't pay the network tax. Every database call is a file I/O operation, not a TCP round-trip. On an SSD, this is blazing fast.

For a platform that runs entirely on your machine, this means agents can query the knowledge graph, log metrics, and store mission state without the latency of a network call.

## The trade-offs

We're not naive about SQLite's limitations:

- **Write contention** — Only one writer at a time per database file. We mitigate this by giving each service its own database file, so they never compete.
- **Scale** — SQLite isn't designed for multi-node clustering. But Evershade is designed for a single machine, so this isn't a problem.
- **Size** — SQLite struggles with databases larger than a few gigabytes. For an AI agent platform, this is more than enough — the knowledge graph, metrics, and logs are all well under this limit.

## When you might want something else

If you're running Evershade in a multi-node cluster or need shared state across machines, you'll want to swap SQLite for PostgreSQL. We're working on an abstraction layer that makes this swap straightforward — the same code, different storage backend.

But for 95% of users — developers running Evershade on their laptop or a single server — SQLite is the right choice.

## The SQLite revival

We're not alone in this. A growing number of projects are choosing SQLite:

- **Turso** — A distributed SQLite platform for edge computing
- **LibSQL** — An open-source fork of SQLite with replication
- **Cloudflare D1** — SQLite as a managed service

The trend is clear: SQLite is having a moment, and for good reason. It's simple, reliable, and fast — everything a self-hosted platform needs.

## Looking ahead

We're exploring full-text search extensions for the knowledge graph and WAL (Write-Ahead Logging) mode for better concurrent reads. SQLite's extension ecosystem is surprisingly rich, and we're just getting started.

---

*Want to dive into the schema? Check out our [documentation](https://github.com/LukaG712/Evershade/tree/master/docs) for the full database design.*
