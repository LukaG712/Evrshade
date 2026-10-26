/** Trapper — Browser Use backend implementation.
 *
 * Integrates with the browser-use library for LLM-driven browser automation.
 * This backend is useful for unstructured browsing tasks that cannot be
 * expressed as structured operations.
 */

import { BrowserBackend, BrowserPage } from './browser.js';

export class BrowserUsePage implements BrowserPage {
  constructor(
    private sessionId: string,
    private backendUrl: string,
  ) {}

  async goto(url: string, options?: { timeout?: number }): Promise<void> {
    await this._request('goto', { url, timeout: options?.timeout || 30000 });
  }

  async content(): Promise<string> {
    const result = await this._request('content', {});
    return result.content || '';
  }

  async title(): Promise<string> {
    const result = await this._request('title', {});
    return result.title || '';
  }

  async screenshot(options?: { type?: 'png' | 'jpeg' }): Promise<Buffer> {
    const result = await this._request('screenshot', { type: options?.type || 'png' });
    return Buffer.from(result.data, 'base64');
  }

  async evaluate<T>(pageFunction: string, ...args: unknown[]): Promise<T> {
    const result = await this._request('evaluate', { pageFunction, args });
    return result.result;
  }

  async fill(selector: string, value: string): Promise<void> {
    await this._request('fill', { selector, value });
  }

  async click(selector: string): Promise<void> {
    await this._request('click', { selector });
  }

  async close(): Promise<void> {
    try {
      await this._request('close', {});
    } catch {
      // Ignore close errors
    }
  }

  /** Ask the LLM to perform an action on the page. */
  async act(instruction: string): Promise<string> {
    const result = await this._request('act', { instruction });
    return result.result || '';
  }

  async _request(action: string, data: Record<string, unknown>): Promise<unknown> {
    const response = await fetch(`${this.backendUrl}/api/session/${this.sessionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, ...data }),
    });
    if (!response.ok) {
      throw new Error(`Browser Use request failed: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }
}

export class BrowserUseBackend implements BrowserBackend {
  private backendUrl: string;
  private initialized = false;

  constructor() {
    this.backendUrl = process.env.BROWSER_USE_BACKEND_URL || 'http://localhost:8091';
  }

  async initialize(): Promise<void> {
    try {
      const response = await fetch(`${this.backendUrl}/health`, { signal: AbortSignal.timeout(5000) });
      if (response.ok) {
        this.initialized = true;
      } else {
        throw new Error(`Browser Use backend not healthy: ${response.status}`);
      }
    } catch (err) {
      // Fallback: mark as not initialized but don't fail startup
      console.warn(`Browser Use backend unavailable: ${err}. Structured operations will not work.`);
      this.initialized = false;
    }
  }

  async createPage(): Promise<BrowserPage> {
    if (!this.initialized) {
      throw new Error('Browser Use backend not initialized');
    }
    const response = await fetch(`${this.backendUrl}/api/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    if (!response.ok) {
      throw new Error(`Failed to create Browser Use session: ${response.status}`);
    }
    const data = await response.json();
    return new BrowserUsePage(data.sessionId, this.backendUrl);
  }

  async shutdown(): Promise<void> {
    // No cleanup needed — the remote backend manages its own resources
  }
}
