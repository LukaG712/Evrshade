---
title: 'Getting Started with Evershade: A 5-Minute Tutorial'
date: '2024-11-18'
slug: 'getting-started-tutorial'
excerpt: 'Step-by-step guide from zero to running AI agents on your machine in under five minutes.'
---

Evershade is designed to be up and running in minutes, not hours. Here's how to go from zero to your first AI agent mission.

## Prerequisites

- Docker Desktop installed and running
- Git installed
- An API key for an LLM provider (OpenAI, Anthropic, or use Ollama for local models)

## Step 1: Clone the repository

```bash
git clone https://github.com/LukaG712/Evershade.git
cd Evershade
```

## Step 2: Run the install script

The install script clones all service repositories and sets up the directory structure:

```bash
./install.sh --profile minimal
```

The `minimal` profile installs the 4 core services: Greenie, Slinker, Trapper, and Gobber. Use `--profile full` for all 10 services.

## Step 3: Configure your environment

Copy the example environment file and set your LLM provider:

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key-here
LLM_MODEL=gpt-4o
```

## Step 4: Start the platform

```bash
./start.sh --profile minimal
```

You'll see Docker containers starting up. Once all services are healthy, open http://localhost:5173 to access the Slammer dashboard.

## Step 5: Create your first mission

In the Slammer dashboard:

1. Click "New Mission"
2. Describe what you want to build
3. Choose an autonomy level (we recommend "partial" for your first run)
4. Click "Start"

Greenie will plan the mission, break it into milestones and features, and assign them to Slinker workers. You'll see real-time logs streaming in the dashboard.

## What happens next?

- **Greenie** plans the mission using Shrewd (LLM) and pulls context from Gobber
- **Slinker** workers execute features in isolated containers
- **Trapper** fetches any web resources needed
- **Hider** manages secrets for API calls
- **Sneaker** records metrics, traces, and logs

When a feature reaches an approval gate, you'll be notified in the dashboard. Review the changes and approve or reject them.

## Troubleshooting

- **Services won't start**: Check Docker Desktop is running and you have enough RAM (4GB minimum)
- **LLM calls fail**: Verify your API key in `.env`
- **Dashboard not loading**: Wait 30 seconds after start for all services to be healthy

## Next steps

- Explore the [glossary](#glossary) to learn Evershade terminology
- Read about the [microservices architecture](#microservices-architecture)
- Check the [FAQ](#faq) for common questions

Welcome to Evershade!
