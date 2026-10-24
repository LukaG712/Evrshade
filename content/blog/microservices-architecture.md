---
title: "How We Built Evershade's Microservices Architecture"
date: "2026-10-20"
slug: "microservices-architecture"
excerpt: "Why we chose 10 independent microservices, how they communicate, and the trade-offs we made along the way."
---

When we started designing Evershade, we knew one thing for certain: we didn't want to build another monolith. The AI agent space is flooded with single-binary tools that try to do everything, and while they work fine for simple tasks, they break down when you need flexibility, observability, or the ability to swap out components.

So we built Evershade as 10 independent microservices, each with a single responsibility. Here's why that decision matters, and how it all holds together.

## The problem with monoliths

Most AI coding tools are monolithic by design. You install one thing, and it handles everything: code completion, file editing, terminal commands, memory, and orchestration. This works until you hit a wall.

Maybe you want to swap out the memory backend. Maybe you need to add custom approval gates before your agents touch production code. Maybe you just want the observability layer without the rest. With a monolith, you're stuck. You either fork the entire project or live with what you've got.

## Our 10 services

Evershade is split into 10 services that fall into three tiers:

**The Orchestrator** — Greenie is the brain. It routes requests, manages agent lifecycles, and coordinates the other services. Nothing talks to the outside world without going through Greenie.

**Core Services** — Slinker handles code operations, Trapper manages errors and exceptions, and Gobber stores everything in a knowledge graph. These are the services that run on every Evershade instance.

**Optional Services** — Shrewd provides model routing, Sneaker handles observability, Hider manages encrypted secrets, Poltergeist processes webhooks, Slammer powers the web dashboard, and Speedy is the CLI. You can run Evershade with just the orchestrator and core services, then add the rest as you need them.

## How they talk

Every service communicates over HTTP on localhost. No message queues, no service mesh, no Kubernetes. Just plain REST APIs between containers.

This simplicity is intentional. We wanted Evershade to run on a developer's laptop with Docker Compose, not require a full DevOps team to deploy. Each service exposes a health endpoint, so Greenie can check if its dependencies are alive before routing requests.

## The trade-offs

Microservices on a single machine is an unusual choice, and it comes with costs:

- **Startup time** — All 10 services need to initialize. We optimized this with health checks and parallel startup, but it's still slower than a single binary.
- **Debugging** — A request that touches 5 services generates logs across 5 containers. That's why Sneaker (observability) is built-in, not an afterthought.
- **Resource usage** — Each service has its own process and memory footprint. On a machine with 8GB RAM, you'll want to run a subset of services.

But the benefits outweigh these costs. You can update one service without restarting the others. You can scale the observability layer independently. You can swap out the knowledge graph backend without touching the orchestrator.

## Why this matters for AI agents

AI agents are inherently unpredictable. They make decisions, call tools, and generate code — all at runtime. A monolithic architecture means every decision path goes through the same codebase, making it hard to reason about what's happening.

With microservices, each decision point is isolated. When an agent calls a tool, that request flows through specific services with clear boundaries. You can trace exactly which service did what, when, and why.

## Looking ahead

We're exploring plugin support for the optional services, so the community can build custom tools that plug into Evershade without modifying the core. The architecture is designed for it — each service has a well-defined API contract that plugins can implement.

The goal is simple: an AI agent platform that's as modular as the problems it solves.

---

*Have questions about the architecture? Check out our [GitHub repo](https://github.com/LukaG712/Evershade) or join the discussion in our [Discord](https://discord.gg/evershade).*
