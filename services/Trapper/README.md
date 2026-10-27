# Trapper

Web scraping and crawling API. Turn websites into clean, LLM-ready data with scraping, crawling, and browser automation.

[MIT License](LICENSE) · TypeScript 5.0+ · Node.js 18+ · Fastify

---

Trapper is a self-hosted web scraping and crawling API that turns websites into clean, LLM-ready data. Scrape single pages, recursively crawl entire sites, and discover URLs — all returning clean markdown, HTML, and structured metadata.

**Features:**

- Single-page scraping with markdown, HTML, links, screenshots, and metadata
- Recursive crawling as async jobs with polling and webhooks
- Batch scraping of multiple URLs simultaneously
- URL discovery via sitemaps and link extraction
- Web search via DuckDuckGo or SearXNG
- Live browser interaction (click, type, scroll, execute JS)
- LLM-powered structured data extraction with JSON schema
- Prompt-driven research agent
- Page actions before scraping (click, scroll, wait, screenshot)
- Theme extraction (colors, fonts, logo)
- Headless browser for SPA/JS-heavy pages
- PDF text extraction
- Full-page screenshots and mobile viewport mode
- Prometheus metrics at `/metrics`

---

## Quick Start

### With Docker

```bash
docker compose up -d Trapper
```

### Direct

```bash
npm install
npx playwright install chromium
npm run dev
```

The API is available at `http://localhost:3000`. Swagger UI at `/docs`.

---

## API Reference

All endpoints require `Authorization: Bearer <API_KEY>` except `/health` and `/metrics`.

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /metrics` | Prometheus metrics |
| `POST /scrape` | Scrape a single URL |
| `POST /crawl` | Start a crawl job |
| `GET /crawl/:jobId` | Check crawl status |
| `DELETE /crawl/:jobId` | Cancel crawl job |
| `POST /map` | Discover URLs on a site |
| `POST /batch_scrape` | Start batch scrape job |
| `GET /batch_scrape/:jobId` | Check batch status |
| `POST /search` | Search and scrape results |
| `POST /interact` | Click, type, scroll in browser |
| `POST /extract` | Start extraction job |
| `GET /extract/:jobId` | Check extraction status |
| `POST /agent` | Start research agent job |
| `GET /agent/:jobId` | Check agent status |

**Scrape a URL:**

```bash
curl -X POST http://localhost:3000/scrape \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "formats": ["markdown", "html"]}'
```

**Start a crawl:**

```bash
curl -X POST http://localhost:3000/crawl \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "maxDiscoveryDepth": 3, "limit": 50}'
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | API server port |
| `HOST` | `0.0.0.0` | Bind address |
| `API_KEY` | *(required)* | Bearer token for API authentication |
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `RATE_LIMIT_MAX` | `60` | Max requests per window |
| `SCRAPE_TIMEOUT` | `30000` | Scrape timeout (ms) |
| `CRAWL_MAX_DEPTH` | `10` | Default max crawl depth |
| `CRAWL_MAX_PAGES` | `100` | Default max pages per crawl |
| `CRAWL_MAX_CONCURRENCY` | `5` | Default concurrent scrapes |
| `BROWSER_HEADLESS` | `true` | Run browser in headless mode |
| `LLM_PROVIDER` | *(none)* | LLM provider for JSON extraction |
| `OPENAI_API_KEY` | *(none)* | OpenAI API key |
| `SEARCH_PROVIDER` | `google` | Search provider (`google`, `searxng`) |

---

## FAQ

**What is Trapper's role in Evershade?**
The web scraping and crawling API for turning websites into clean, LLM-ready data.

**Does Trapper respect robots.txt?**
Yes. The crawler honors robots.txt rules with caching. Override with `ignoreRobotsTxt: true`.

**How do I handle JavaScript-rendered pages?**
Trapper automatically falls back to a headless Playwright browser when HTTP fetch returns insufficient content.

**Can I interact with pages after scraping?**
Yes. Use `/interact` to click, type, scroll, and execute JavaScript. Sessions persist for 30 minutes.

---

## Support & Community

| Channel | Purpose |
|---------|---------|
| [GitHub Issues](https://github.com/LukaG712/Trapper/issues) | Bug reports and feature requests |
| [Evershade Docs](https://github.com/LukaG712/Evershade) | Comprehensive guides and references |
| [Discussions](https://github.com/LukaG712/Evershade/discussions) | Community discussions and Q&A |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> **Disclaimer:** This project is a fan-made, independent software project. It is not affiliated with, endorsed by, or in any way connected to Nintendo, Next Level Games, or any of their subsidiaries. All Luigi's Mansion trademarks and character names are property of their respective owners. Service names are used purely for thematic inspiration.
