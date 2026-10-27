# Shrewd

LLM provider abstraction layer. Unified interface for OpenAI, Anthropic, Google Gemini, and Ollama with cost tracking and privacy classification.

[MIT License](LICENSE) · Python 3.10+ · FastAPI

---

Shrewd is the LLM provider abstraction service for the Evershade ecosystem. It provides a unified interface for multiple LLM providers with model routing, cost tracking, privacy classification, and OpenTelemetry tracing.

**Features:**

- Multi-provider support: OpenAI, Anthropic, Google Gemini, Ollama
- 17+ pre-configured models with context window and privacy metadata
- Automatic model routing based on model name
- Per-request cost tracking with token usage
- Privacy classification: public (cloud) vs private (local)
- Cost summary with aggregated stats by provider and model
- Provider availability checks
- Prometheus metrics at `/metrics`
- OpenTelemetry distributed tracing

---

## Quick Start

### With Docker

```bash
docker compose up -d Shrewd
```

### Direct

```bash
pip install -e ".[dev]"
python -m uvicorn shrewd.api:app --host 0.0.0.0 --port 8089
```

The API is available at `http://localhost:8089`. Swagger UI at `/docs`.

---

## API Reference

All endpoints require `Authorization: Bearer <API_KEY>` except `/health` and `/metrics`.

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /metrics` | Prometheus metrics |
| `POST /api/chat` | Route a chat request to an LLM provider |
| `GET /api/models` | List available models |
| `GET /api/providers` | List providers with status |
| `GET /api/cost/summary` | Get cost and usage statistics |

**Send a chat request:**

```bash
curl -X POST http://localhost:8089/api/chat \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Explain quantum computing"}], "temperature": 0.7}'
```

**Privacy-aware request (local only):**

```bash
curl -X POST http://localhost:8089/api/chat \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1", "messages": [{"role": "user", "content": "Analyze data"}], "require_private": true}'
```

---

## Model Registry

| Provider | Models | Privacy |
|----------|--------|---------|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-3.5-turbo | Public |
| Anthropic | claude-3-opus, claude-3-sonnet, claude-3-haiku | Public |
| Google | gemini-pro, gemini-1.5-pro, gemini-1.5-flash | Public |
| Ollama | llama3, llama3.1, llama3.2, gemma2, mistral, phi3 | Private |

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | *(required)* | Bearer token for API authentication |
| `PORT` | `8089` | Server port |
| `SHREWD_DEFAULT_MODEL` | `llama3` | Default model when none specified |
| `OPENAI_API_KEY` | *(none)* | OpenAI API key |
| `ANTHROPIC_API_KEY` | *(none)* | Anthropic API key |
| `GOOGLE_API_KEY` | *(none)* | Google AI API key |
| `OLLAMA_URL` | `http://host.docker.internal:11434` | Ollama API endpoint |
| `SNEAKER_OTLP_ENDPOINT` | *(none)* | Sneaker OTLP endpoint for tracing |

---

## FAQ

**What is Shrewd's role in Evershade?**
The LLM provider abstraction layer with model routing, cost tracking, and privacy classification.

**Which providers are supported?**
OpenAI, Anthropic, Google AI, and Ollama (local models). Configure multiple providers simultaneously.

**How do I track LLM costs?**
Shrewd automatically tracks token usage and estimated costs. Query `GET /api/cost/summary`.

**How do I keep data private?**
Use `require_private: true` in chat requests with an Ollama model. Shrewd rejects public models with this flag.

**Can I use a local LLM?**
Yes. Configure Ollama by setting `OLLAMA_URL` and pulling a model locally (`ollama pull llama3.1`).

---

## Support & Community

| Channel | Purpose |
|---------|---------|
| [GitHub Issues](https://github.com/LukaG712/Shrewd/issues) | Bug reports and feature requests |
| [Evershade Docs](https://github.com/LukaG712/Evershade) | Comprehensive guides and references |
| [Discussions](https://github.com/LukaG712/Evershade/discussions) | Community discussions and Q&A |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> **Disclaimer:** This project is a fan-made, independent software project. It is not affiliated with, endorsed by, or in any way connected to Nintendo, Next Level Games, or any of their subsidiaries. All Luigi's Mansion trademarks and character names are property of their respective owners. Service names are used purely for thematic inspiration.
