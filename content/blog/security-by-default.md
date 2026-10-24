---
title: "Security by Default: Approval Gates and the Autonomy Dial"
date: "2026-10-10"
slug: "security-by-default"
excerpt: "How Evershade keeps you in control of your AI agents, from approval gates to encrypted secrets."
---

AI agents are powerful. They can read your code, modify files, run commands, and access your APIs. That power comes with responsibility — and risk.

Most AI coding tools give agents free rein. They trust the model to do the right thing, and hope for the best. Evershade takes a different approach: security by default, with controls that let you dial autonomy up or down at any time.

## Approval gates

Approval gates are Evershade's primary security mechanism. Before an agent performs any action that could affect your system, it stops and asks for your permission.

By default, Evershade requires approval for:

- **File modifications** — Creating, editing, or deleting files
- **Command execution** — Running terminal commands
- **API calls** — Making external HTTP requests
- **Database changes** — Modifying SQLite databases

When an agent hits an approval gate, it pauses and presents you with a summary of what it wants to do. You can approve, reject, or modify the action before it proceeds.

This isn't a checkbox you click once and forget. Every significant action requires explicit consent, so you're always in the loop.

## The autonomy dial

Not every task needs the same level of oversight. That's why Evershade includes an autonomy dial — a safety level you can adjust based on your comfort and the task at hand.

**Level 0: Full control** — Every action, no matter how small, requires your approval. This is the safest setting, ideal for learning or working on critical code.

**Level 1: High oversight** — Only significant actions (file modifications, command execution) require approval. Read operations and analysis are automatic.

**Level 2: Balanced** — Only destructive actions (deleting files, running commands with side effects) require approval. Most code modifications are automatic.

**Level 3: Autonomous** — Agents work freely, but still respect sandboxed execution and secrets encryption. You can review everything afterward in the observability dashboard.

You can change the autonomy level at any time, even mid-mission. Start conservative, then dial it up as you build trust.

## Sandboxed execution

Even with approval gates, you don't want agents running commands directly on your host machine. That's why Evershade uses sandboxed execution.

When an agent runs a terminal command, it executes inside a Docker container with:

- **No network access** — Unless you explicitly grant it
- **Read-only filesystem** — Unless you explicitly grant write access
- **Resource limits** — CPU and memory caps to prevent runaway processes
- **Timeout** — Commands that run too long are automatically killed

This means even if an agent makes a mistake — or gets compromised — the damage is contained.

## Secrets encryption

API keys, database passwords, tokens — these are sensitive. Evershade's Hider service encrypts all secrets with AES-256 before storing them in SQLite.

Secrets are never logged, never sent to external services, and never exposed in the dashboard. When an agent needs a secret, Hider decrypts it in memory and passes it directly to the service that needs it.

You manage secrets through the CLI or the dashboard, and they're encrypted at rest. Even if someone gains access to your SQLite files, they can't read your secrets without the encryption key.

## Prompt injection defense

AI models are vulnerable to prompt injection — where malicious input tricks the model into doing something unintended. Evershade defends against this with:

- **Input sanitization** — All user input is scanned for known injection patterns
- **System prompt isolation** — The system prompt is separated from user input, making it harder to override
- **Output validation** — Agent outputs are checked for suspicious patterns before execution

No defense is perfect, but these layers make prompt injection significantly harder.

## No telemetry

Evershade doesn't collect telemetry. We don't know how many people are running it, what models they're using, or what tasks they're doing. Your usage data stays on your machine, period.

This isn't just a privacy feature — it's a security feature. The less data that leaves your machine, the less attack surface there is.

## Looking ahead

We're working on several security enhancements:

- **Role-based access** — Different autonomy levels for different agents
- **Audit logs** — A complete history of every approval, rejection, and action
- **Policy engine** — Custom rules like "never modify files in /prod" or "always approve database changes"
- **Multi-signature approval** — Require multiple people to approve high-risk actions

Security isn't a feature you add at the end. It's a foundation you build from the start. With Evershade, you're always in control — your agents work for you, not against you.

---

*Want to learn more about Evershade's security model? Check out our [documentation](https://github.com/LukaG712/Evershade/tree/master/docs) or the [compare page](/compare).*
