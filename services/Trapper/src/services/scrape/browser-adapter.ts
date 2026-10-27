/**
 * Browser automation adapter pattern.
 *
 * Defines a common interface for browser backends so that alternative
 * implementations (e.g., Playwright MCP, Browser Use) can be swapped
 * in without modifying core scrape/crawl code.
 *
 * Configuration:
 *   TRAPPER_BROWSER_BACKEND=playwright  (default)
 */

import { Action } from '../../utils/types';

export interface BrowserBackend {
  /** Unique identifier for this backend implementation. */
  readonly name: string;

  /** Initialize the backend (launch browser, connect to remote, etc.). */
  initialize(): Promise<void>;

  /** Shutdown and release all resources. */
  shutdown(): Promise<void>;

  /**
   * Scrape a single URL and return the rendered content.
   */
  scrape(
    url: string,
    options: BrowserScrapeOptions
  ): Promise<BackendScrapeResult>;

  /**
   * Create a persistent interactive session.
   */
  createSession(): Promise<BrowserSession>;
}

export interface BackendScrapeResult {
  html: string;
  title: string;
  screenshot?: string;
  statusCode?: number;
  actionsResult?: BackendActionsResult;
}

export interface BrowserSession {
  /** Unique session identifier. */
  readonly id: string;

  /** Navigate to a URL. */
  goto(url: string): Promise<void>;

  /** Execute a sequence of actions (click, type, scroll, etc.). */
  executeActions(actions: Action[]): Promise<BackendActionsResult>;

  /** Capture a screenshot. */
  screenshot(): Promise<string | undefined>;

  /** Get the current page HTML. */
  getHtml(): Promise<string>;

  /** Get the current page title. */
  getTitle(): Promise<string>;

  /** Close the session and release resources. */
  close(): Promise<void>;
}

export interface BackendActionsResult {
  results: Array<{ action: string; success: boolean; error?: string }>;
}

export interface BrowserScrapeOptions {
  waitFor?: number;
  timeout?: number;
  headers?: Record<string, string>;
  blockAds?: boolean;
  screenshot?: boolean;
  mobile?: boolean;
  actions?: Action[];
}

/**
 * Factory that returns the configured browser backend.
 */
export async function createBrowserBackend(): Promise<BrowserBackend> {
  const backend = process.env.TRAPPER_BROWSER_BACKEND || 'playwright';

  switch (backend.toLowerCase()) {
    case 'playwright': {
      const { PlaywrightBackend } = await import('./playwright-backend');
      return new PlaywrightBackend();
    }
    default:
      throw new Error(`Unknown browser backend: ${backend}`);
  }
}
