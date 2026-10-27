/**
 * Playwright implementation of the BrowserBackend adapter.
 *
 * Wraps the existing Playwright browser automation code behind the
 * BrowserBackend interface so that alternative backends can be
 * substituted without modifying core scrape/crawl logic.
 */

import { chromium, Browser, BrowserContext, Page } from 'playwright';
import { v4 as uuidv4 } from 'uuid';
import config from '../../config';
import logger from '../../utils/logger';
import { Action } from '../../utils/types';
import { executeActions } from './actions';
import {
  browserSessionsActive,
  browserSessionsCreatedTotal,
} from '../../utils/metrics';

import {
  BrowserBackend,
  BrowserSession as AdapterBrowserSession,
  BrowserScrapeOptions,
  BackendScrapeResult,
  BackendActionsResult,
} from './browser-adapter';

let browser: Browser | null = null;

// Session storage for /interact endpoint
interface BrowserSessionInternal {
  context: BrowserContext;
  page: Page;
  createdAt: number;
}

const sessions = new Map<string, BrowserSessionInternal>();
const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
const MAX_SESSIONS = 100;

// Periodic cleanup of expired sessions
let cleanupTimer: NodeJS.Timeout | null = null;

export function startSessionCleanup(): void {
  if (cleanupTimer) return;
  cleanupTimer = setInterval(async () => {
    await cleanupExpiredSessions();
  }, 5 * 60 * 1000);
  cleanupTimer.unref?.();
  logger.info('Session cleanup timer started');
}

export function stopSessionCleanup(): void {
  if (cleanupTimer) {
    clearInterval(cleanupTimer);
    cleanupTimer = null;
    logger.info('Session cleanup timer stopped');
  }
}

async function cleanupExpiredSessions(): Promise<void> {
  const now = Date.now();
  for (const [id, session] of sessions.entries()) {
    if (now - session.createdAt > SESSION_TIMEOUT_MS) {
      await session.page.close();
      await session.context.close();
      sessions.delete(id);
      browserSessionsActive.dec();
      logger.info(`Cleaned up expired session ${id}`);
    }
  }
}

async function getBrowser(): Promise<Browser> {
  if (!browser) {
    browser = await chromium.launch({
      headless: config.browser.headless,
      timeout: config.browser.launchTimeout,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-software-rasterizer',
      ],
    });
    logger.info('Browser launched');
  }
  return browser;
}

async function getContext(options?: { mobile?: boolean }): Promise<BrowserContext> {
  const brow = await getBrowser();
  const viewport = options?.mobile
    ? { width: 375, height: 812 }
    : { width: 1280, height: 800 };

  return await brow.newContext({
    userAgent: options?.mobile
      ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
      : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport,
  });
}


class PlaywrightSession implements AdapterBrowserSession {
  readonly id: string;
  private _context: BrowserContext;
  private _page: Page;

  constructor(context: BrowserContext, page: Page) {
    this.id = uuidv4();
    this._context = context;
    this._page = page;
    sessions.set(this.id, { context, page, createdAt: Date.now() });
    browserSessionsActive.inc();
    browserSessionsCreatedTotal.inc();
  }

  async goto(url: string): Promise<void> {
    await this._page.goto(url, { waitUntil: 'domcontentloaded' });
  }

  async executeActions(actions: Action[]): Promise<BackendActionsResult> {
    const result = await executeActions(this._page, actions);
    // Convert ActionsResult to BackendActionsResult
    const converted: BackendActionsResult = {
      results: actions.map((a, i) => ({
        action: a.type,
        success: true,
      })),
    };
    return converted;
  }

  async screenshot(): Promise<string | undefined> {
    const buf = await this._page.screenshot({ type: 'jpeg', quality: 80 });
    return buf.toString('base64');
  }

  async getHtml(): Promise<string> {
    return await this._page.content();
  }

  async getTitle(): Promise<string> {
    return await this._page.title();
  }

  async close(): Promise<void> {
    await this._page.close();
    await this._context.close();
    sessions.delete(this.id);
    browserSessionsActive.dec();
  }
}


export class PlaywrightBackend implements BrowserBackend {
  readonly name = 'playwright';

  async initialize(): Promise<void> {
    await getBrowser();
  }

  async shutdown(): Promise<void> {
    // Close all active sessions
    for (const [id, session] of sessions.entries()) {
      await session.page.close().catch(() => {});
      await session.context.close().catch(() => {});
      sessions.delete(id);
      browserSessionsActive.dec();
    }
    if (browser) {
      await browser.close();
      browser = null;
      logger.info('Browser closed');
    }
  }

  async scrape(url: string, options: BrowserScrapeOptions = {}): Promise<BackendScrapeResult> {
    const context = await getContext({ mobile: options.mobile });
    const page: Page = await context.newPage();

    try {
      const timeout = options.timeout || config.scrape.timeout;

      if (options.headers) {
        await page.setExtraHTTPHeaders(options.headers);
      }

      if (options.mobile) {
        await page.setViewportSize({ width: 375, height: 812 });
      }

      if (options.blockAds) {
        await page.route('**/*', async (route) => {
          const reqUrl = route.request().url();
          const adPatterns = [
            '/ads/',
            'doubleclick.net',
            'adservice.',
            'adsystem.',
            'adnxs.com',
            'adservice.google',
          ];
          if (adPatterns.some((p) => reqUrl.includes(p))) {
            route.abort();
          } else {
            route.continue();
          }
        });
      }

      const response = await page.goto(url, {
        waitUntil: 'domcontentloaded',
        timeout,
      });

      if (options.waitFor) {
        await page.waitForTimeout(options.waitFor);
      }

      let actionsResult: BackendActionsResult | undefined;
      if (options.actions && options.actions.length > 0) {
        const result = await executeActions(page, options.actions);
        actionsResult = {
          results: options.actions.map((a) => ({
            action: a.type,
            success: true,
          })),
        };
      }

      const html = await page.content();
      const title = await page.title();

      let screenshot: string | undefined;
      if (options.screenshot) {
        const buf = await page.screenshot({ type: 'jpeg', quality: 80 });
        screenshot = buf.toString('base64');
      }

      return {
        html,
        title,
        screenshot,
        statusCode: response?.status(),
        actionsResult,
      };
    } finally {
      await context.close();
    }
  }

  async createSession(): Promise<AdapterBrowserSession> {
    if (sessions.size >= MAX_SESSIONS) {
      // Clean up expired sessions first
      await cleanupExpiredSessions();
      if (sessions.size >= MAX_SESSIONS) {
        throw new Error('Maximum number of sessions reached');
      }
    }

    const context = await getContext();
    const page = await context.newPage();
    return new PlaywrightSession(context, page);
  }
}

// Re-export session management for the server
export { sessions, SESSION_TIMEOUT_MS, MAX_SESSIONS };
