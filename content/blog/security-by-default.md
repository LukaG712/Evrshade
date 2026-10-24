---
title: 'Security by Default: Approval Gates and the Autonomy Dial'
date: '2024-11-25'
slug: 'security-by-default'
excerpt: 'How Evershade keeps you in control with approval gates, autonomy levels, and container isolation.'
---

AI agents that can modify your codebase need guardrails. Evershade puts you in control at every level.

## Approval gates

An approval gate is a checkpoint where the agent pauses and waits for your explicit permission before proceeding. By default, Evershade requires approval for:

- **File modifications** — Any change to source code
- **Git operations** — Commits, pushes, branch creation
- **Secret access** — Reading API keys or credentials
- **Network calls** — External HTTP requests beyond the platform

You review the proposed changes in the Slammer dashboard and approve or reject them.

## The autonomy dial

Not every task needs the same level of oversight. Evershade's autonomy dial lets you choose:

- **Full autonomy** — Agents act without approval (for trusted, read-only tasks)
- **Partial autonomy** — Agents act but require approval for sensitive operations (the default)
- **No autonomy** — Every action requires approval (maximum safety)

You can set the autonomy level per mission or globally in `.env`.

## Container isolation

Every Slinker worker runs in its own Docker container with:

- A fresh filesystem
- No access to the host machine
- Limited network permissions
- Resource limits (CPU, memory)

Even if an agent goes rogue, it's contained.

## Encrypted secrets

Hider manages all secrets with AES-256-GCM encryption at rest. Secrets are never logged, never sent to external services, and are only decrypted when needed by the requesting service.

## Injection defenses

Shrewd, the LLM abstraction layer, includes prompt injection defenses:

- Input sanitization before sending to the LLM
- Output validation before executing agent responses
- System prompt isolation to prevent override attacks

## Conclusion

Security isn't an afterthought in Evershade — it's built into every layer. You decide how much control to give agents, and the platform enforces those boundaries.
