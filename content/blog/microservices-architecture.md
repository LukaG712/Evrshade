---
title: "How We Built Evershade's Microservices Architecture"
date: "2024-11-15"
slug: "microservices-architecture"
excerpt: "Why we chose 10 independent services, how they communicate, and the trade-offs we made along the way."
---

When we started designing Evershade, we knew one thing for certain: a monolithic AI agent platform wouldn't scale — either technically or conceptually.

## The problem with monoliths

Most AI coding tools are built as single applications. They bundle code generation, execution, memory, and UI into one process. This works until you want to swap out one piece without breaking the others.

We wanted a platform where you could:

- Replace the LLM provider without touching the code executor
- Add a new service without redeploying the whole stack
- Run just the services you need on limited hardware

## Ten services, one platform

Evershade is built as 10 independent microservices:

1. **Greenie** — The orchestrator and API backend
2. **Slinker** — Code execution engine
3. **Trapper** — Web scraping and crawling
4. **Gobber** — Persistent storage and knowledge graph
5. **Shrewd** — LLM provider abstraction
6. **Sneaker** — Metrics, traces, and logs
7. **Hider** — Encrypted secrets management
8. **Poltergeist** — Notifications and async delivery
9. **Slammer** — React web dashboard
10. **Speedy** — The CLI

Each service has a single responsibility, talks over HTTP, and can run independently.

## Communication pattern

Services communicate through simple HTTP REST APIs. No message queues, no event buses, no distributed databases. If a service is down, the others keep running — the platform degrades gracefully.

Greenie is the only orchestrator. It coordinates missions by calling other services in sequence. Every other service is a leaf node with no dependencies on its siblings.

## The trade-offs

Microservices add complexity. You need to manage multiple processes, handle network failures, and reason about distributed state. But for Evershade, the benefits outweigh the costs:

- **Modularity** — Each service can be developed, tested, and deployed independently
- **Resource efficiency** — Run only what you need
- **Fault isolation** — One service crashing doesn't take down the platform
- **Extensibility** — Add new services without modifying existing ones

## SQLite-first

Despite being distributed, each service uses SQLite for persistence. No PostgreSQL, no MongoDB, no Redis (except for Trapper's caching). SQLite is fast, reliable, and requires zero configuration — it's the perfect fit for a self-hosted platform.

## Conclusion

The microservices architecture is what makes Evershade unique. It's not just an AI coding tool — it's a platform you can extend, modify, and adapt to your workflow.
