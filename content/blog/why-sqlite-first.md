---
title: 'Why SQLite-First?'
date: '2024-11-20'
slug: 'why-sqlite-first'
excerpt: 'Why SQLite is the primary storage layer for an AI agent platform — and why it works better than you might expect.'
---

When people hear "microservices," they expect PostgreSQL, MongoDB, or at least Redis. Evershade uses SQLite for everything. Here's why.

## The self-hosted constraint

Evershade runs on ordinary developer hardware. Requiring a separate database server adds complexity, memory overhead, and a single point of failure. SQLite eliminates all three.

## Zero configuration

With SQLite, there's no database server to install, no connection strings to configure, no user permissions to manage. The database is a file. That's it.

```
DATABASE_URL=sqlite:///data/greenie.db
```

## Performance

SQLite is fast. For read-heavy workloads (which is what most AI agent platforms are), SQLite often outperforms client-server databases because there's no network overhead.

## One database per service

Each Evershade service has its own SQLite file. Greenie has `greenie.db`, Gobber has `gobber.db`, and so on. This matches the microservices philosophy: each service owns its data.

## WAL mode for concurrency

SQLite's Write-Ahead Logging (WAL) mode allows concurrent reads while writes are happening. This is perfect for Evershade's workload: Sneaker writes metrics while Slammer reads them in real time.

## Backups are trivial

Back up your Evershade instance? Copy the `data/` directory. That's a complete snapshot. No `pg_dump`, no `mongodump`, no complex backup procedures.

## When SQLite isn't enough

For Trapper's caching layer, we do use Redis. But that's the exception, not the rule. For 95% of Evershade's storage needs, SQLite is the right tool.

## Conclusion

SQLite-first isn't a compromise — it's a design decision. It keeps Evershade simple, fast, and truly self-hosted without requiring infrastructure expertise.
