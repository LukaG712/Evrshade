import Fastify from 'fastify';
import cors from '@fastify/cors';
import rateLimit from '@fastify/rate-limit';
import { apiKeyAuth } from './middleware/auth';
import { registerScrapeRoutes } from './routes/scrape';
import { registerCrawlRoutes } from './routes/crawl';
import { registerMapRoutes } from './routes/map';
import { registerBatchScrapeRoutes } from './routes/batchScrape';
import { registerSearchRoutes } from './routes/search';
import { registerInteractRoutes } from './routes/interact';
import { registerExtractRoutes } from './routes/extract';
import { registerAgentRoutes } from './routes/agent';
import config from '../config';
import logger from '../utils/logger';
import {
  register,
  httpRequestDurationSeconds,
  httpRequestsTotal,
  httpActiveRequests,
} from '../utils/metrics';

const app = Fastify({
  logger: {
    level: config.logLevel,
  },
});

async function bootstrap() {
  // Validate API key at startup
  if (!config.apiKey) {
    logger.error('API_KEY environment variable is not set. Refusing to start Trapper.');
    process.exit(1);
  }

  // Register plugins
  await app.register(cors, {
    origin: process.env.CORS_ORIGIN || ['http://localhost', 'http://localhost:8080', 'http://localhost:3000'],
    credentials: true,
  });

  await app.register(rateLimit, {
    max: config.rateLimit.max,
    timeWindow: config.rateLimit.windowMs,
    keyGenerator: (request) => {
      return request.headers.authorization || request.ip;
    },
  });

  // Health check (no auth required)
  app.get('/health', async () => {
    return { status: 'ok', timestamp: new Date().toISOString() };
  });

  // Prometheus metrics endpoint (no auth required)
  app.get('/metrics', async () => {
    return register.metrics();
  });

  // HTTP metrics hooks
  app.addHook('onRequest', async (request) => {
    httpActiveRequests.inc();
  });

  app.addHook('onSend', async (request, _reply, _payload) => {
    const start = (request as any).startTime;
    if (start) {
      const duration = (Date.now() - start) / 1000;
      const route = request.routeOptions.url || request.url;
      const status = request.raw.statusCode?.toString() || '200';
      httpRequestDurationSeconds
        .labels(request.method, route, status)
        .observe(duration);
      httpRequestsTotal.labels(request.method, route, status).inc();
    }
    httpActiveRequests.dec();
  });

  // Track start time for duration measurement
  app.addHook('onRequest', async (request) => {
    (request as any).startTime = Date.now();
  });

  // Capabilities (no auth required)
  app.get('/api/capabilities', async () => {
    return {
      service: 'Trapper',
      version: '1.1.0',
      features: [
        'scraping',
        'crawling',
        'batch_scraping',
        'extraction',
        'interaction',
        'mapping',
        'search',
        'browser_automation',
        'agent_queue',
        'ssrf_protection',
        'prometheus_metrics',
      ],
    };
  });

  // Register routes (before auth hook so health/capabilities are not protected)
  registerScrapeRoutes(app);
  registerCrawlRoutes(app);
  registerMapRoutes(app);
  registerBatchScrapeRoutes(app);
  registerSearchRoutes(app);
  registerInteractRoutes(app);
  registerExtractRoutes(app);
  registerAgentRoutes(app);

  // Apply auth to all API routes (skip health check only)
  app.addHook('onRequest', async (request, reply) => {
    // Skip auth for health check only
    if (request.url === '/health') {
      return;
    }
    await apiKeyAuth(request, reply, () => {});
  });

  // Error handler
  app.setErrorHandler((error, request, reply) => {
    logger.error(`Unhandled error: ${error.message}`);
    reply.code(500).send({
      success: false,
      error: 'Internal server error',
    });
  });

  return app;
}

export async function startServer() {
  await bootstrap();

  try {
    await app.listen({
      port: config.port,
      host: config.host,
    });
    logger.info(`Server listening on http://${config.host}:${config.port}`);
  } catch (err) {
    logger.error(`Failed to start server: ${(err as Error).message}`);
    process.exit(1);
  }
}

export { app };
