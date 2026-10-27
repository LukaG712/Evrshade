import Fastify, { FastifyInstance } from 'fastify';

describe('Server API', () => {
  let server: FastifyInstance;

  beforeAll(async () => {
    // Build a test server without starting it
    server = Fastify({ logger: false });

    // Register the same routes as the real server
    const cors = await import('@fastify/cors');
    await server.register(cors.default, { origin: true, credentials: true });

    // Health check (no auth) — registered BEFORE auth hook
    server.get('/health', async () => {
      return { status: 'ok', timestamp: expect.any(String) };
    });

    // Apply auth hook to all routes AFTER health
    server.addHook('onRequest', async (request: any, reply: any) => {
      // Skip health check
      if (request.url === '/health') return;
      const { apiKeyAuth } = await import('../../src/api/middleware/auth');
      await apiKeyAuth(request, reply, () => {});
    });

    // Register scrape route
    const { registerScrapeRoutes } = await import('../../src/api/routes/scrape');
    registerScrapeRoutes(server);

    // Register search route
    const { registerSearchRoutes } = await import('../../src/api/routes/search');
    registerSearchRoutes(server);

    // Register map route
    const { registerMapRoutes } = await import('../../src/api/routes/map');
    registerMapRoutes(server);

    await server.ready();
  });

  afterAll(async () => {
    await server.close();
  });

  describe('Health Check', () => {
    it('returns ok status without auth', async () => {
      const response = await server.inject({
        method: 'GET',
        url: '/health',
      });

      expect(response.statusCode).toBe(200);
      const body = JSON.parse(response.payload);
      expect(body.status).toBe('ok');
      expect(body.timestamp).toBeDefined();
    });
  });

  describe('Authentication', () => {
    it('rejects requests without API key', async () => {
      const response = await server.inject({
        method: 'POST',
        url: '/scrape',
        payload: { url: 'https://example.com' },
      });

      expect(response.statusCode).toBe(401);
      const body = JSON.parse(response.payload);
      expect(body.success).toBe(false);
      expect(body.error).toContain('Authorization');
    });

    it('rejects requests with invalid API key', async () => {
      const response = await server.inject({
        method: 'POST',
        url: '/scrape',
        headers: { authorization: 'Bearer wrong-key' },
        payload: { url: 'https://example.com' },
      });

      expect(response.statusCode).toBe(401);
      const body = JSON.parse(response.payload);
      expect(body.success).toBe(false);
      expect(body.error).toBe('Invalid API key');
    });

    it('accepts requests with valid Bearer token', async () => {
      const apiKey = process.env.API_KEY || 'test-key';
      const response = await server.inject({
        method: 'POST',
        url: '/scrape',
        headers: { authorization: `Bearer ${apiKey}` },
        payload: { url: 'not-a-url' },
      });

      // Should pass auth and fail on URL validation
      expect(response.statusCode).toBe(400);
    });

    it('rejects requests with api-key query param (Bearer only)', async () => {
      const apiKey = process.env.API_KEY || 'test-key';
      const response = await server.inject({
        method: 'POST',
        url: `/scrape?api-key=${apiKey}`,
        payload: { url: 'not-a-url' },
      });

      expect(response.statusCode).toBe(401);
    });
  });

  describe('Scrape Route Validation', () => {
    const validKey = process.env.API_KEY || 'test-key';

    it('rejects missing URL', async () => {
      const response = await server.inject({
        method: 'POST',
        url: '/scrape',
        headers: { authorization: `Bearer ${validKey}` },
        payload: {},
      });

      expect(response.statusCode).toBe(400);
      const body = JSON.parse(response.payload);
      expect(body.error).toBe('URL is required');
    });

    it('rejects invalid URL format', async () => {
      const response = await server.inject({
        method: 'POST',
        url: '/scrape',
        headers: { authorization: `Bearer ${validKey}` },
        payload: { url: 'not-a-url' },
      });

      expect(response.statusCode).toBe(400);
      const body = JSON.parse(response.payload);
      expect(body.error).toBe('Invalid URL format');
    });
  });

  describe('Search Route Validation', () => {
    const validKey = process.env.API_KEY || 'test-key';

    it('rejects missing query', async () => {
      const response = await server.inject({
        method: 'POST',
        url: '/search',
        headers: { authorization: `Bearer ${validKey}` },
        payload: {},
      });

      expect(response.statusCode).toBe(400);
      const body = JSON.parse(response.payload);
      expect(body.error).toBe('Search query is required');
    });
  });

  describe('Map Route Validation', () => {
    const validKey = process.env.API_KEY || 'test-key';

    it('rejects missing URL', async () => {
      const response = await server.inject({
        method: 'POST',
        url: '/map',
        headers: { authorization: `Bearer ${validKey}` },
        payload: {},
      });

      expect(response.statusCode).toBe(400);
      const body = JSON.parse(response.payload);
      expect(body.error).toBe('URL is required');
    });

    it('rejects invalid URL format', async () => {
      const response = await server.inject({
        method: 'POST',
        url: '/map',
        headers: { authorization: `Bearer ${validKey}` },
        payload: { url: 'invalid-url' },
      });

      expect(response.statusCode).toBe(400);
      const body = JSON.parse(response.payload);
      expect(body.error).toBe('Invalid URL format');
    });
  });

  describe('Metrics', () => {
    it('exposes prom-client metrics module', async () => {
      const metrics = await import('../../src/utils/metrics');
      expect(metrics.register).toBeDefined();
      expect(metrics.httpRequestDurationSeconds).toBeDefined();
      expect(metrics.httpRequestsTotal).toBeDefined();
      expect(metrics.httpActiveRequests).toBeDefined();
      expect(metrics.scrapeRequestsTotal).toBeDefined();
      expect(metrics.scrapeDurationSeconds).toBeDefined();
      expect(metrics.crawlJobsTotal).toBeDefined();
      expect(metrics.crawlDurationSeconds).toBeDefined();
      expect(metrics.crawlPagesTotal).toBeDefined();
      expect(metrics.crawlErrorsTotal).toBeDefined();
      expect(metrics.browserSessionsActive).toBeDefined();
      expect(metrics.browserSessionsCreatedTotal).toBeDefined();
      expect(metrics.queueJobsTotal).toBeDefined();
      expect(metrics.queueDepth).toBeDefined();
    });

    it('metrics register produces Prometheus text format', async () => {
      const { register } = await import('../../src/utils/metrics');
      const metricsText = await register.metrics();
      // Should contain default Node.js metrics collected by prom-client
      expect(metricsText).toContain('# HELP');
      expect(metricsText).toContain('# TYPE');
      // Should contain process CPU time metric from collectDefaultMetrics
      expect(metricsText).toContain('process_cpu');
    });
  });
});
