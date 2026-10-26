/** Trapper — Scraping, crawling, browser automation, and research routes. */

import { FastifyInstance, FastifyReply, FastifyRequest } from 'fastify';
import { BrowserBackend, ResearchQuery, ResearchResult, ResearchSession } from './browser.js';
import { ResearchEngine } from './research.js';
import { isUrlSafe } from './ssrf.js';
import { rateLimiter } from './rateLimit.js';

export async function registerRoutes(fastify: FastifyInstance, backend: BrowserBackend, researchEngine?: ResearchEngine) {

  // ─── Scrape a single URL ───────────────────────────────────────────────

  fastify.post('/api/scrape', async (request: FastifyRequest, reply: FastifyReply) => {
    const rl = rateLimiter.check((request as any).ip || 'unknown');
    if (!rl.allowed) {
      return reply.code(429).send({
        error: 'RATE_LIMITED',
        message: 'Rate limit exceeded',
        retryAfter: Math.ceil((rl.resetAt - Date.now()) / 1000),
      });
    }

    const body = (request as any).body as Record<string, unknown>;
    const url = typeof body.url === 'string' ? body.url : '';
    if (!url) {
      return reply.code(400).send({ error: 'VALIDATION_ERROR', message: 'url is required' });
    }

    if (!isUrlSafe(url)) {
      return reply.code(400).send({ error: 'SSRF_BLOCKED', message: 'URL is not allowed (SSRF protection)' });
    }

    try {
      const page = await backend.createPage();
      await page.goto(url, { timeout: Number(body.timeout) || 30000 });

      const html = await page.content();
      const title = await page.title();

      // Extract text content
      const text = await page.evaluate(() => {
        const el = document.body.cloneNode(true) as HTMLElement;
        el.querySelectorAll('script, style, noscript, iframe').forEach((e) => e.remove());
        return el.textContent || '';
      });

      await page.close();

      return reply.code(200).send({
        url,
        title,
        html: body.includeHtml !== false ? html : undefined,
        text,
        status: 'success',
      });
    } catch (err: any) {
      return reply.code(500).send({
        error: 'SCRAPE_FAILED',
        message: err.message || 'Failed to scrape URL',
      });
    }
  });

  // ─── Extract structured data ───────────────────────────────────────────

  fastify.post('/api/extract', async (request: FastifyRequest, reply: FastifyReply) => {
    const rl = rateLimiter.check((request as any).ip || 'unknown');
    if (!rl.allowed) {
      return reply.code(429).send({
        error: 'RATE_LIMITED',
        message: 'Rate limit exceeded',
        retryAfter: Math.ceil((rl.resetAt - Date.now()) / 1000),
      });
    }

    const body = (request as any).body as Record<string, unknown>;
    const url = typeof body.url === 'string' ? body.url : '';
    const selectors = Array.isArray(body.selectors) ? body.selectors : [];

    if (!url) {
      return reply.code(400).send({ error: 'VALIDATION_ERROR', message: 'url is required' });
    }
    if (!isUrlSafe(url)) {
      return reply.code(400).send({ error: 'SSRF_BLOCKED', message: 'URL is not allowed (SSRF protection)' });
    }

    try {
      const page = await backend.createPage();
      await page.goto(url, { timeout: Number(body.timeout) || 30000 });

      const results: Record<string, unknown>[] = [];
      for (const sel of selectors) {
        const selector = typeof sel === 'string' ? sel : (sel as any).selector || '';
        const attr = typeof sel === 'string' ? null : (sel as any).attribute || null;
        const items = await page.evaluate((s, a) => {
          const els = document.querySelectorAll(s);
          return Array.from(els).map((el) => {
            if (a) return el.getAttribute(a);
            return el.textContent?.trim() || '';
          });
        }, selector, attr);
        results.push({ selector, items });
      }

      await page.close();

      return reply.code(200).send({ url, results, status: 'success' });
    } catch (err: any) {
      return reply.code(500).send({
        error: 'EXTRACT_FAILED',
        message: err.message || 'Failed to extract data',
      });
    }
  });

  // ─── Crawl a site (synchronous, limited depth) ─────────────────────────

  fastify.post('/api/crawl', async (request: FastifyRequest, reply: FastifyReply) => {
    const rl = rateLimiter.check((request as any).ip || 'unknown');
    if (!rl.allowed) {
      return reply.code(429).send({
        error: 'RATE_LIMITED',
        message: 'Rate limit exceeded',
        retryAfter: Math.ceil((rl.resetAt - Date.now()) / 1000),
      });
    }

    const body = (request as any).body as Record<string, unknown>;
    const url = typeof body.url === 'string' ? body.url : '';
    const maxDepth = Math.min(Number(body.maxDepth) || 2, 5);
    const maxPages = Math.min(Number(body.maxPages) || 20, 100);

    if (!url) {
      return reply.code(400).send({ error: 'VALIDATION_ERROR', message: 'url is required' });
    }
    if (!isUrlSafe(url)) {
      return reply.code(400).send({ error: 'SSRF_BLOCKED', message: 'URL is not allowed (SSRF protection)' });
    }

    const visited = new Set<string>();
    const pages: Array<{ url: string; title: string; depth: number }> = [];

    async function crawl(currentUrl: string, depth: number) {
      if (visited.has(currentUrl) || depth > maxDepth || pages.length >= maxPages) return;
      visited.add(currentUrl);

      try {
        const page = await backend.createPage();
        await page.goto(currentUrl, { timeout: 15000 });
        const title = await page.title();
        pages.push({ url: currentUrl, title, depth });

        if (depth < maxDepth && pages.length < maxPages) {
          const links = await page.evaluate((baseUrl) => {
            const els = document.querySelectorAll('a[href]');
            return Array.from(els)
              .map((a) => {
                try {
                  return new URL(a.getAttribute('href')!, baseUrl).href;
                } catch {
                  return null;
                }
              })
              .filter((u): u is string => u !== null && (u.startsWith('http:') || u.startsWith('https:')));
          }, currentUrl);

          await page.close();

          // Deduplicate and filter
          const uniqueLinks = [...new Set(links)].filter((l) => !visited.has(l) && isUrlSafe(l));
          for (const link of uniqueLinks.slice(0, 10)) {
            if (pages.length >= maxPages) break;
            await crawl(link, depth + 1);
          }
        } else {
          await page.close();
        }
      } catch {
        // Skip failed pages
      }
    }

    await crawl(url, 0);

    return reply.code(200).send({
      startUrl: url,
      pages,
      pageCount: pages.length,
      status: 'success',
    });
  });

  // ─── Map a site (return link structure only) ───────────────────────────

  fastify.post('/api/map', async (request: FastifyRequest, reply: FastifyReply) => {
    const rl = rateLimiter.check((request as any).ip || 'unknown');
    if (!rl.allowed) {
      return reply.code(429).send({
        error: 'RATE_LIMITED',
        message: 'Rate limit exceeded',
        retryAfter: Math.ceil((rl.resetAt - Date.now()) / 1000),
      });
    }

    const body = (request as any).body as Record<string, unknown>;
    const url = typeof body.url === 'string' ? body.url : '';
    if (!url) {
      return reply.code(400).send({ error: 'VALIDATION_ERROR', message: 'url is required' });
    }
    if (!isUrlSafe(url)) {
      return reply.code(400).send({ error: 'SSRF_BLOCKED', message: 'URL is not allowed (SSRF protection)' });
    }

    try {
      const page = await backend.createPage();
      await page.goto(url, { timeout: 15000 });

      const map = await page.evaluate((baseUrl) => {
        const els = document.querySelectorAll('a[href]');
        return Array.from(els).map((a) => {
          const href = a.getAttribute('href')!;
          let absolute: string;
          try {
            absolute = new URL(href, baseUrl).href;
          } catch {
            absolute = href;
          }
          return {
            text: a.textContent?.trim()?.slice(0, 200) || '',
            href: absolute,
          };
        });
      }, url);

      await page.close();

      return reply.code(200).send({ url, links: map, linkCount: map.length, status: 'success' });
    } catch (err: any) {
      return reply.code(500).send({
        error: 'MAP_FAILED',
        message: err.message || 'Failed to map URL',
      });
    }
  });

  // ─── Search (keyword search on page) ───────────────────────────────────

  fastify.post('/api/search', async (request: FastifyRequest, reply: FastifyReply) => {
    const rl = rateLimiter.check((request as any).ip || 'unknown');
    if (!rl.allowed) {
      return reply.code(429).send({
        error: 'RATE_LIMITED',
        message: 'Rate limit exceeded',
        retryAfter: Math.ceil((rl.resetAt - Date.now()) / 1000),
      });
    }

    const body = (request as any).body as Record<string, unknown>;
    const url = typeof body.url === 'string' ? body.url : '';
    const query = typeof body.query === 'string' ? body.query : '';

    if (!url || !query) {
      return reply.code(400).send({ error: 'VALIDATION_ERROR', message: 'url and query are required' });
    }
    if (!isUrlSafe(url)) {
      return reply.code(400).send({ error: 'SSRF_BLOCKED', message: 'URL is not allowed (SSRF protection)' });
    }

    try {
      const page = await backend.createPage();
      await page.goto(url, { timeout: 15000 });

      const results = await page.evaluate((q) => {
        const text = document.body.textContent || '';
        const lower = text.toLowerCase();
        const qlower = q.toLowerCase();
        const indices: number[] = [];
        let idx = lower.indexOf(qlower);
        while (idx !== -1) {
          indices.push(idx);
          idx = lower.indexOf(qlower, idx + 1);
        }
        const context = 100;
        return indices.slice(0, 10).map((i) => ({
          position: i,
          context: text.slice(Math.max(0, i - context), i + q.length + context).trim(),
        }));
      }, query);

      await page.close();

      return reply.code(200).send({ url, query, results, resultCount: results.length, status: 'success' });
    } catch (err: any) {
      return reply.code(500).send({
        error: 'SEARCH_FAILED',
        message: err.message || 'Failed to search URL',
      });
    }
  });

  // ─── Interact (fill forms, click buttons) ──────────────────────────────

  fastify.post('/api/interact', async (request: FastifyRequest, reply: FastifyReply) => {
    const rl = rateLimiter.check((request as any).ip || 'unknown');
    if (!rl.allowed) {
      return reply.code(429).send({
        error: 'RATE_LIMITED',
        message: 'Rate limit exceeded',
        retryAfter: Math.ceil((rl.resetAt - Date.now()) / 1000),
      });
    }

    const body = (request as any).body as Record<string, unknown>;
    const url = typeof body.url === 'string' ? body.url : '';
    const actions = Array.isArray(body.actions) ? body.actions : [];

    if (!url) {
      return reply.code(400).send({ error: 'VALIDATION_ERROR', message: 'url is required' });
    }
    if (!isUrlSafe(url)) {
      return reply.code(400).send({ error: 'SSRF_BLOCKED', message: 'URL is not allowed (SSRF protection)' });
    }

    try {
      const page = await backend.createPage();
      await page.goto(url, { timeout: 15000 });

      const results: Array<{ action: string; status: string }> = [];
      for (const act of actions) {
        const a = act as Record<string, string>;
        try {
          if (a.type === 'fill') {
            await page.fill(a.selector!, a.value!);
            results.push({ action: `fill ${a.selector}`, status: 'ok' });
          } else if (a.type === 'click') {
            await page.click(a.selector!);
            results.push({ action: `click ${a.selector}`, status: 'ok' });
          } else if (a.type === 'wait') {
            await new Promise((r) => setTimeout(r, Number(a.duration) || 1000));
            results.push({ action: `wait ${a.duration}ms`, status: 'ok' });
          } else {
            results.push({ action: a.type || 'unknown', status: 'unsupported' });
          }
        } catch (err: any) {
          results.push({ action: a.type || 'unknown', status: `error: ${err.message}` });
        }
      }

      const finalContent = await page.content();
      await page.close();

      return reply.code(200).send({ url, results, finalContent, status: 'success' });
    } catch (err: any) {
      return reply.code(500).send({
        error: 'INTERACT_FAILED',
        message: err.message || 'Failed to interact with URL',
      });
    }
  });

  // ─── Screenshot ────────────────────────────────────────────────────────

  fastify.post('/api/screenshot', async (request: FastifyRequest, reply: FastifyReply) => {
    const rl = rateLimiter.check((request as any).ip || 'unknown');
    if (!rl.allowed) {
      return reply.code(429).send({
        error: 'RATE_LIMITED',
        message: 'Rate limit exceeded',
        retryAfter: Math.ceil((rl.resetAt - Date.now()) / 1000),
      });
    }

    const body = (request as any).body as Record<string, unknown>;
    const url = typeof body.url === 'string' ? body.url : '';
    if (!url) {
      return reply.code(400).send({ error: 'VALIDATION_ERROR', message: 'url is required' });
    }
    if (!isUrlSafe(url)) {
      return reply.code(400).send({ error: 'SSRF_BLOCKED', message: 'URL is not allowed (SSRF protection)' });
    }

    try {
      const page = await backend.createPage();
      await page.goto(url, { timeout: 15000 });
      const screenshot = await page.screenshot({ type: 'png' });
      await page.close();

      reply.header('Content-Type', 'image/png');
      return reply.code(200).send(screenshot);
    } catch (err: any) {
      return reply.code(500).send({
        error: 'SCREENSHOT_FAILED',
        message: err.message || 'Failed to take screenshot',
      });
    }
  });

  // ─── Research Routes ───────────────────────────────────────────────────

  if (researchEngine) {
    // Create a new research task
    fastify.post('/api/research', async (request: FastifyRequest, reply: FastifyReply) => {
      const rl = rateLimiter.check((request as any).ip || 'unknown');
      if (!rl.allowed) {
        return reply.code(429).send({
          error: 'RATE_LIMITED',
          message: 'Rate limit exceeded',
          retryAfter: Math.ceil((rl.resetAt - Date.now()) / 1000),
        });
      }

      const body = (request as any).body as Record<string, unknown>;
      const query = typeof body.query === 'string' ? body.query : '';
      if (!query) {
        return reply.code(400).send({ error: 'VALIDATION_ERROR', message: 'query is required' });
      }

      const researchQuery: ResearchQuery = {
        query,
        urls: Array.isArray(body.urls) ? (body.urls as string[]) : undefined,
        maxPages: Number(body.maxPages) || undefined,
        maxDepth: Number(body.maxDepth) || undefined,
        extractionRules: Array.isArray(body.extractionRules) ? (body.extractionRules as string[]) : undefined,
        timeout: Number(body.timeout) || undefined,
      };

      // Validate URLs for SSRF
      if (researchQuery.urls) {
        for (const url of researchQuery.urls) {
          if (!isUrlSafe(url)) {
            return reply.code(400).send({
              error: 'SSRF_BLOCKED',
              message: `URL is not allowed (SSRF protection): ${url}`,
            });
          }
        }
      }

      const sessionId = researchEngine.createSession(researchQuery);

      // Start research in background
      researchEngine.executeResearch(sessionId, researchQuery).catch((err) => {
        fastify.log.error(`Research task failed: ${err.message}`);
      });

      return reply.code(201).send({
        sessionId,
        status: 'pending',
        message: 'Research task created',
      });
    });

    // Get research session status
    fastify.get('/api/research/:sessionId', async (request: FastifyRequest, reply: FastifyReply) => {
      const sessionId = (request as any).params.sessionId as string;
      const session = researchEngine.getSession(sessionId);

      if (!session) {
        return reply.code(404).send({ error: 'NOT_FOUND', message: 'Research session not found' });
      }

      return reply.code(200).send(session);
    });

    // Get research result
    fastify.get('/api/research/:sessionId/result', async (request: FastifyRequest, reply: FastifyReply) => {
      const sessionId = (request as any).params.sessionId as string;

      const session = researchEngine.getSession(sessionId);
      if (!session) {
        return reply.code(404).send({ error: 'NOT_FOUND', message: 'Research session not found' });
      }

      if (session.status === 'running' || session.status === 'pending') {
        return reply.code(202).send({
          status: session.status,
          progress: session.progress,
          message: 'Research still in progress',
        });
      }

      const result = researchEngine.getResult(sessionId);
      if (!result) {
        return reply.code(404).send({ error: 'NOT_FOUND', message: 'Research result not found' });
      }

      return reply.code(200).send(result);
    });

    // Cancel research session
    fastify.post('/api/research/:sessionId/cancel', async (request: FastifyRequest, reply: FastifyReply) => {
      const sessionId = (request as any).params.sessionId as string;
      const cancelled = researchEngine.cancelSession(sessionId);

      if (!cancelled) {
        return reply.code(400).send({ error: 'CANCEL_FAILED', message: 'Cannot cancel this session' });
      }

      return reply.code(200).send({ status: 'cancelled', message: 'Research session cancelled' });
    });

    // List active research sessions
    fastify.get('/api/research/sessions', async (_request: FastifyRequest, reply: FastifyReply) => {
      const sessions = researchEngine.listSessions();
      return reply.code(200).send({ sessions, count: sessions.length });
    });
  }
}
