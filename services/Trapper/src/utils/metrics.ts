import * as promClient from 'prom-client';

// Register a default metrics registry
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

// ---------------------------------------------------------------------------
// HTTP request metrics
// ---------------------------------------------------------------------------

const httpRequestDurationSeconds = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30],
  registers: [register],
});

const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status'],
  registers: [register],
});

const httpActiveRequests = new promClient.Gauge({
  name: 'http_active_requests',
  help: 'Number of currently active HTTP requests',
  registers: [register],
});

// ---------------------------------------------------------------------------
// Scrape metrics
// ---------------------------------------------------------------------------

const scrapeRequestsTotal = new promClient.Counter({
  name: 'trapper_scrape_requests_total',
  help: 'Total number of scrape requests',
  labelNames: ['outcome', 'use_browser'],
  registers: [register],
});

const scrapeDurationSeconds = new promClient.Histogram({
  name: 'trapper_scrape_duration_seconds',
  help: 'Duration of scrape operations in seconds',
  labelNames: ['use_browser'],
  buckets: [0.1, 0.5, 1, 2.5, 5, 10, 30, 60],
  registers: [register],
});

const scrapePagesTotal = new promClient.Counter({
  name: 'trapper_scrape_pages_total',
  help: 'Total number of pages scraped',
  registers: [register],
});

// ---------------------------------------------------------------------------
// Crawl metrics
// ---------------------------------------------------------------------------

const crawlJobsTotal = new promClient.Counter({
  name: 'trapper_crawl_jobs_total',
  help: 'Total number of crawl jobs',
  labelNames: ['outcome'],
  registers: [register],
});

const crawlDurationSeconds = new promClient.Histogram({
  name: 'trapper_crawl_duration_seconds',
  help: 'Duration of crawl jobs in seconds',
  buckets: [5, 10, 30, 60, 120, 300, 600],
  registers: [register],
});

const crawlPagesTotal = new promClient.Counter({
  name: 'trapper_crawl_pages_total',
  help: 'Total number of pages crawled',
  registers: [register],
});

const crawlErrorsTotal = new promClient.Counter({
  name: 'trapper_crawl_errors_total',
  help: 'Total number of crawl errors',
  registers: [register],
});

// ---------------------------------------------------------------------------
// Browser session metrics
// ---------------------------------------------------------------------------

const browserSessionsActive = new promClient.Gauge({
  name: 'trapper_browser_sessions_active',
  help: 'Number of active browser sessions',
  registers: [register],
});

const browserSessionsCreatedTotal = new promClient.Counter({
  name: 'trapper_browser_sessions_created_total',
  help: 'Total number of browser sessions created',
  registers: [register],
});

const browserScrapesTotal = new promClient.Counter({
  name: 'trapper_browser_scrapes_total',
  help: 'Total number of browser-based scrapes',
  labelNames: ['outcome'],
  registers: [register],
});

// ---------------------------------------------------------------------------
// Queue metrics
// ---------------------------------------------------------------------------

const queueJobsTotal = new promClient.Counter({
  name: 'trapper_queue_jobs_total',
  help: 'Total number of queue jobs processed',
  labelNames: ['queue', 'outcome'],
  registers: [register],
});

const queueDepth = new promClient.Gauge({
  name: 'trapper_queue_depth',
  help: 'Current depth of job queues',
  labelNames: ['queue'],
  registers: [register],
});

// ---------------------------------------------------------------------------
// Content extraction metrics
// ---------------------------------------------------------------------------

const extractJobsTotal = new promClient.Counter({
  name: 'trapper_extract_jobs_total',
  help: 'Total number of extract jobs',
  labelNames: ['outcome'],
  registers: [register],
});

// ---------------------------------------------------------------------------
// Agent metrics
// ---------------------------------------------------------------------------

const agentJobsTotal = new promClient.Counter({
  name: 'trapper_agent_jobs_total',
  help: 'Total number of agent jobs',
  labelNames: ['outcome'],
  registers: [register],
});

const agentDurationSeconds = new promClient.Histogram({
  name: 'trapper_agent_duration_seconds',
  help: 'Duration of agent jobs in seconds',
  buckets: [5, 10, 30, 60, 120, 300, 600],
  registers: [register],
});

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

export {
  register,
  httpRequestDurationSeconds,
  httpRequestsTotal,
  httpActiveRequests,
  scrapeRequestsTotal,
  scrapeDurationSeconds,
  scrapePagesTotal,
  crawlJobsTotal,
  crawlDurationSeconds,
  crawlPagesTotal,
  crawlErrorsTotal,
  browserSessionsActive,
  browserSessionsCreatedTotal,
  browserScrapesTotal,
  queueJobsTotal,
  queueDepth,
  extractJobsTotal,
  agentJobsTotal,
  agentDurationSeconds,
};
