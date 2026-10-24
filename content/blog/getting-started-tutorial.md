---
title: "Getting Started with Evershade: A 5-Minute Tutorial"
date: "2026-10-18"
slug: "getting-started-tutorial"
excerpt: "From zero to running AI agents on your machine in under 5 minutes. Here's the step-by-step guide."
---

You've heard about Evershade. Now you want to run it. This guide will get you from a blank terminal to a fully functional AI agent platform in under 5 minutes.

## Prerequisites

Before we start, make sure you have:

- **Docker Desktop** installed and running (free for individuals)
- **8GB RAM** available (4GB minimum, but 8GB is recommended)
- **20GB disk space** for Docker images and SQLite databases
- An **LLM API key** (OpenAI, Anthropic, or any OpenAI-compatible provider)

That's it. No cloud accounts, no subscriptions, no vendor lock-in.

## Step 1: Clone the repository

Open your terminal and run:

```bash
git clone https://github.com/LukaG712/Evershade.git
cd Evershade
```

This downloads the entire Evershade platform, including the Docker Compose configuration, all 10 microservices, and the documentation.

## Step 2: Configure your API key

Evershade uses environment variables for configuration. Copy the example file:

```bash
cp .env.example .env
```

Then open `.env` and add your API key:

```
EVERSHADE_API_KEY=sk-your-key-here
EVERSHADE_MODEL_PROVIDER=openai
EVERSHADE_MODEL=gpt-4o
```

You can use any OpenAI-compatible provider. If you're using Ollama for local models, set:

```
EVERSHADE_API_KEY=
EVERSHADE_MODEL_PROVIDER=ollama
EVERSHADE_MODEL=llama3
EVERSHADE_API_BASE=http://host.docker.internal:11434
```

## Step 3: Start the platform

This is the magic command:

```bash
docker compose up -d
```

Docker will pull the images and start all 10 services in the background. On first run, this takes about 2 minutes as it downloads the images. Subsequent starts are nearly instant.

You can check the status with:

```bash
docker compose ps
```

You should see all services in the `healthy` state.

## Step 4: Open the dashboard

Evershade includes a web dashboard called Slammer. Open your browser and navigate to:

```
http://localhost:3000
```

You'll see the Evershade dashboard with real-time metrics, agent status, and a terminal interface.

## Step 5: Run your first agent

In the dashboard, click "New Mission" and type a task:

```
Refactor the authentication module to use JWT tokens instead of session cookies.
```

Evershade will:

1. **Analyze** the request through Greenie (the orchestrator)
2. **Search** your codebase using Slinker
3. **Plan** the changes with the selected LLM
4. **Execute** the refactoring with approval gates
5. **Log** everything to Sneaker for observability

You'll see the agent's progress in real-time, with each step clearly labeled.

## What just happened?

Behind the scenes, Evershade's microservices worked together:

- **Greenie** orchestrated the entire mission
- **Slinker** analyzed and modified your code
- **Trapper** caught and reported any errors
- **Gobber** stored the mission context in the knowledge graph
- **Sneaker** logged metrics, traces, and structured logs
- **Slammer** displayed everything in the dashboard

## Next steps

Now that you're running, here's what to explore:

- **The CLI** — Try `speedy mission create "your task"` from the terminal
- **Approval gates** — Configure safety levels in `.env` to control agent autonomy
- **Knowledge graph** — Check how Gobber remembers context across sessions
- **Observability** — Dive into Sneaker's metrics and traces

## Troubleshooting

**Services won't start?** Check `docker compose logs` for error messages.

**Out of memory?** Reduce the number of services in `docker-compose.yml` by commenting out optional ones.

**API key errors?** Verify your `.env` file and restart with `docker compose restart`.

## Join the community

Stuck? Want to share what you built? Join our [Discord](https://discord.gg/evershade) or check out the [documentation](https://github.com/LukaG712/Evershade/tree/master/docs).

---

*Welcome to Evershade. Your agents. Your hardware. Your data.*
