/** Trapper — Playwright MCP backend implementation.
 *
 * Integrates with Microsoft's Playwright MCP server for MCP-standard
 * browser operations. Useful when agents need to drive the browser
 * through MCP rather than direct API calls.
 */

import { BrowserBackend, BrowserPage } from './browser.js';

export class PlaywrightMcpPage implements BrowserPage {
  constructor(
    private contextId: string,
    private backendUrl: string,
  ) {}

  async goto(url: string, options?: { timeout?: number }): Promise<void> {
    await this._mcpCall('browser_navigate', { url, timeout: options?.timeout || 30000 });
  }

  async content(): Promise<string> {
    const result = await this._mcpCall('browser_snapshot', {});
    return result.content || '';
  }

  async title(): Promise<string> {
    const result = await this._mcpCall('browser_get_text', { selector: 'title' });
    return result.text || '';
  }

  async screenshot(options?: { type?: 'png' | 'jpeg' }): Promise<Buffer> {
    const result = await this._mcpCall('browser_screenshot', { format: options?.type || 'png' });
    return Buffer.from(result.data, 'base64');
  }

  async evaluate<T>(pageFunction: string, ...args: unknown[]): Promise<T> {
    const result = await this._mcpCall('browser_evaluate', { pageFunction, args });
    return result.result;
  }

  async fill(selector: string, value: string): Promise<void> {
    await this._mcpCall('browser_fill', { selector, value });
  }

  async click(selector: string): Promise<void> {
    await this._mcpCall('browser_click', { selector });
  }

  async close(): Promise<void> {
    try {
      await this._mcpCall('browser_close_context', { contextId: this.contextId });
    } catch {
      // Ignore close errors
    }
  }

  async _mcpCall(method: string, params: Record<string, unknown>): Promise<unknown> {
    const response = await fetch(`${this.backendUrl}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: Date.now(),
        method: `browser/${method}`,
        params: { contextId: this.contextId, ...params },
      }),
    });
    if (!response.ok) {
      throw new Error(`Playwright MCP request failed: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    if (data.error) {
      throw new Error(`MCP error: ${data.error.message}`);
    }
    return data.result || {};
  }
}

export class PlaywrightMcpBackend implements BrowserBackend {
  private backendUrl: string;
  private initialized = false;

  constructor() {
    this.backendUrl = process.env.PLAYWRIGHT_MCP_BACKEND_URL || 'http://localhost:8092';
  }

  async initialize(): Promise<void> {
    try {
      const response = await fetch(`${this.backendUrl}/health`, { signal: AbortSignal.timeout(5000) });
      if (response.ok) {
        this.initialized = true;
      } else {
        throw new Error(`Playwright MCP backend not healthy: ${response.status}`);
      }
    } catch (err) {
      // Fallback: mark as not initialized but don't fail startup
      console.warn(`Playwright MCP backend unavailable: ${err}. Structured operations will not work.`);
      this.initialized = false;
    }
  }

  async createPage(): Promise<BrowserPage> {
    if (!this.initialized) {
      throw new Error('Playwright MCP backend not initialized');
    }
    const response = await fetch(`${this.backendUrl}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'browser/new_context',
        params: {},
      }),
    });
    if (!response.ok) {
      throw new Error(`Failed to create Playwright MCP context: ${response.status}`);
    }
    const data = await response.json();
    if (data.error) {
      throw new Error(`MCP error: ${data.error.message}`);
    }
    const contextId = data.result?.contextId || `ctx-${Date.now()}`;
    return new PlaywrightMcpPage(contextId, this.backendUrl);
  }

  async shutdown(): Promise<void> {
    // No cleanup needed — the remote backend manages its own resources
  }
}
