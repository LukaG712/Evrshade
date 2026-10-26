/** Trapper — Web scraping, crawling, browser automation, and research. */

import Fastify from 'fastify';
import cors from '@fastify/cors';
import { BrowserBackend } from './browser.js';
import { PlaywrightBackend } from './playwrightBackend.js';
import { ResearchEngine } from './research.js';
import { registerRoutes } from './routes.js';

const VERSION = '2.0.0';
const PORT = Number(process.env.PORT) || 3000;

// Browser backend selection
const BACKEND_TYPE = process.env.TRAPPER_BROWSER_BACKEND || 'playwright';

// Lazy-load optional backends to avoid crashing if they're unavailable
let BrowserUseBackend: new () => BrowserBackend | undefined;
let PlaywrightMcpBackend: new () => BrowserBackend | undefined;

async function loadOptionalBackends() {
  try {
    const mod = await import('./browserUseBackend.js');
    BrowserUseBackend = mod.BrowserUseBackend;
  } catch {
    console.warn('Browser Use backend not available — will fall back to Playwright');
  }
  try {
    const mod = await import('./playwrightMcpBackend.js');
    PlaywrightMcpBackend = mod.PlaywrightMcpBackend;
  } catch {
    console.warn('Playwright MCP backend not available — will fall back to Playwright');
  }
}

function createBrowserBackend(): BrowserBackend {
  switch (BACKEND_TYPE) {
    case 'playwright':
      return new PlaywrightBackend();
    case 'browser-use': {
      if (!BrowserUseBackend) {
        console.warn('Browser Use requested but not loaded, falling back to Playwright');
        return new PlaywrightBackend();
      }
      return new BrowserUseBackend();
    }
    case 'playwright-mcp': {
      if (!PlaywrightMcpBackend) {
        console.warn('Playwright MCP requested but not loaded, falling back to Playwright');
        return new PlaywrightBackend();
      }
      return new PlaywrightMcpBackend();
    }
    default:
      throw new Error(`Unknown browser backend: ${BACKEND_TYPE}`);
  }
}

const fastify = Fastify({ logger: true });
let backend: BrowserBackend | null = null;
let researchEngine: ResearchEngine | null = null;
let ready = false;

fastify.register(cors, { origin: true });

// ─── Health endpoints ──────────────────────────────────────────────────────

fastify.get('/health', async (_request, reply) => {
  reply.code(200).send({ status: 'ok', service: 'Trapper', version: VERSION });
});

fastify.get('/ready', async (_request, reply) => {
  if (!ready) {
    return reply.code(503).send({ status: 'not_ready', service: 'Trapper' });
  }
  reply.code(200).send({ status: 'ready', service: 'Trapper' });
});

fastify.get('/api/status', async (_request, reply) => {
  reply.code(200).send({
    service: 'Trapper',
    version: VERSION,
    status: ready ? 'running' : 'starting',
    uptimeSeconds: process.uptime(),
    dependencies: {
      browserBackend: BACKEND_TYPE,
      ready,
    },
  });
});

fastify.get('/api/capabilities', async (_request, reply) => {
  reply.code(200).send({
    service: 'Trapper',
    version: VERSION,
    capabilities: [
      'scrape', 'extract', 'crawl', 'map', 'search', 'interact', 'screenshot',
      'research', 'research_sessions',
    ],
    integrations: {
      browserBackend: {
        type: BACKEND_TYPE,
        ready,
      },
      researchEngine: {
        enabled: true,
        maxConcurrentSessions: Number(process.env.TRAPPER_MAX_RESEARCH_SESSIONS) || 10,
      },
    },
  });
});

// ─── Metrics ───────────────────────────────────────────────────────────────

let requestCount = 0;

fastify.get('/metrics', async (_request, reply) => {
  requestCount++;
  const uptime = process.uptime();
  const metrics = [
    `# HELP trapper_uptime_seconds Service uptime in seconds.`,
    `# TYPE trapper_uptime_seconds gauge`,
    `trapper_uptime_seconds ${uptime.toFixed(1)}`,
    `# HELP trapper_requests_total Total HTTP requests.`,
    `# TYPE trapper_requests_total counter`,
    `trapper_requests_total ${requestCount}`,
    `# HELP trapper_ready Service readiness (1=ready, 0=not ready).`,
    `# TYPE trapper_ready gauge`,
    `trapper_ready ${ready ? 1 : 0}`,
  ].join('\n') + '\n';

  reply.header('Content-Type', 'text/plain; version=0.0.4');
  reply.code(200).send(metrics);
});

// ─── Start ─────────────────────────────────────────────────────────────────

async function start() {
  try {
    // Load optional backends (Browser Use, Playwright MCP)
    await loadOptionalBackends();

    // Initialize browser backend
    backend = createBrowserBackend();
    await backend.initialize();

    // Initialize research engine
    const maxSessions = Number(process.env.TRAPPER_MAX_RESEARCH_SESSIONS) || 10;
    researchEngine = new ResearchEngine(backend, maxSessions);

    // Periodic cleanup of old sessions
    setInterval(() => {
      if (researchEngine) {
        researchEngine.cleanup();
      }
    }, 5 * 60 * 1000); // Every 5 minutes

    ready = true;

    // Register business routes
    await registerRoutes(fastify, backend, researchEngine);

    await fastify.listen({ port: PORT, host: '0.0.0.0' });
    fastify.log.info(`Trapper listening on port ${PORT} with backend: ${BACKEND_TYPE}`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
}

// Graceful shutdown
const shutdown = async () => {
  fastify.log.info('Shutting down Trapper...');
  if (backend) {
    await backend.shutdown();
  }
  await fastify.close();
  process.exit(0);
};

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

start();
