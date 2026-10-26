/** Trapper — Playwright browser backend implementation. */

import { chromium, Browser, Page } from 'playwright';
import { BrowserBackend, BrowserPage } from './browser.js';

export class PlaywrightPage implements BrowserPage {
  constructor(private page: Page) {}

  async goto(url: string, options?: { timeout?: number }): Promise<void> {
    await this.page.goto(url, { timeout: options?.timeout || 30000 });
  }

  async content(): Promise<string> {
    return this.page.content();
  }

  async title(): Promise<string> {
    return this.page.title();
  }

  async screenshot(options?: { type?: 'png' | 'jpeg' }): Promise<Buffer> {
    const buf = await this.page.screenshot({ type: options?.type || 'png' });
    return Buffer.from(buf);
  }

  async evaluate<T>(pageFunction: string, ...args: unknown[]): Promise<T> {
    return this.page.evaluate(pageFunction, ...args);
  }

  async fill(selector: string, value: string): Promise<void> {
    await this.page.fill(selector, value);
  }

  async click(selector: string): Promise<void> {
    await this.page.click(selector);
  }

  async close(): Promise<void> {
    await this.page.close();
  }
}

export class PlaywrightBackend implements BrowserBackend {
  private browser: Browser | null = null;

  async initialize(): Promise<void> {
    this.browser = await chromium.launch({
      headless: process.env.PLAYWRIGHT_HEADLESS !== 'false',
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
  }

  async createPage(): Promise<BrowserPage> {
    if (!this.browser) {
      throw new Error('Playwright backend not initialized');
    }
    const context = await this.browser.newContext();
    const page = await context.newPage();
    return new PlaywrightPage(page);
  }

  async shutdown(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }
}
