# Slammer

Web dashboard for the Evershade ecosystem. React-based frontend for managing agents, runs, pipelines, and analytics.

[MIT License](LICENSE) · React · TypeScript · Vite · Tailwind CSS

---

Slammer is the standalone web dashboard for the Evershade ecosystem. It provides a unified view of all services with agent management, pipeline building, analytics, and web crawling.

**Features:**

- Unified dashboard view of all Evershade services
- Agent management — create, configure, and monitor AI agents
- Pipeline builder — visual editor for cross-service workflows
- Analytics — charts and metrics from Sneaker
- Visual web crawler — launch crawl jobs against Trapper with live progress
- Grafana integration — navigation link with live health status

---

## Quick Start

```bash
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_GREENIE_URL` | `http://localhost:8080` | Greenie API URL |
| `VITE_SLINKER_URL` | `http://localhost:8000` | Slinker API URL |
| `VITE_TRAPPER_URL` | `http://localhost:3000` | Trapper API URL |
| `VITE_GRAFANA_URL` | `http://localhost:3000` | Grafana dashboard URL |

---

## FAQ

**What is Slammer's role in Evershade?**
The standalone web dashboard providing a React-based frontend for all services.

**How do I access Grafana from Slammer?**
A Grafana link button appears in the navigation with a live status indicator. Configure via `VITE_GRAFANA_URL`.

**Does Slammer have a /metrics endpoint?**
No. Slammer is a frontend SPA with no HTTP server.

**How do I use the visual web crawler?**
Navigate to the Crawler page, enter a URL, configure options, and start the job. Monitor live progress, inspect results, view screenshots, and export as JSON or CSV.

---

## Support & Community

| Channel | Purpose |
|---------|---------|
| [GitHub Issues](https://github.com/LukaG712/Slammer/issues) | Bug reports and feature requests |
| [Evershade Docs](https://github.com/LukaG712/Evershade) | Comprehensive guides and references |
| [Discussions](https://github.com/LukaG712/Evershade/discussions) | Community discussions and Q&A |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> **Disclaimer:** This project is a fan-made, independent software project. It is not affiliated with, endorsed by, or in any way connected to Nintendo, Next Level Games, or any of their subsidiaries. All Luigi's Mansion trademarks and character names are property of their respective owners. Service names are used purely for thematic inspiration.
