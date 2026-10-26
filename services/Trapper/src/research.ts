/** Trapper — Research engine for agent-requested research tasks. */

import { BrowserBackend, BrowserPage, ResearchQuery, ResearchResult, ResearchSource, ResearchSession } from './browser.js';
import { isUrlSafe } from './ssrf.js';

export class ResearchEngine {
  private backend: BrowserBackend;
  private sessions: Map<string, ResearchSession> = new Map();
  private results: Map<string, ResearchResult> = new Map();
  private maxConcurrentSessions: number;

  constructor(backend: BrowserBackend, maxConcurrentSessions: number = 10) {
    this.backend = backend;
    this.maxConcurrentSessions = maxConcurrentSessions;
  }

  /** Create a new research session. */
  createSession(query: ResearchQuery): string {
    const sessionId = crypto.randomUUID();
    const maxPages = Math.min(query.maxPages || 10, 50);

    const session: ResearchSession = {
      id: sessionId,
      status: 'pending',
      progress: 0,
      pagesVisited: 0,
      maxPages,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    this.sessions.set(sessionId, session);
    return sessionId;
  }

  /** Get research session status. */
  getSession(sessionId: string): ResearchSession | undefined {
    return this.sessions.get(sessionId);
  }

  /** Cancel a research session. */
  cancelSession(sessionId: string): boolean {
    const session = this.sessions.get(sessionId);
    if (!session || session.status === 'completed' || session.status === 'failed') {
      return false;
    }
    session.status = 'cancelled';
    session.updatedAt = new Date().toISOString();
    return true;
  }

  /** Get research result by ID. */
  getResult(resultId: string): ResearchResult | undefined {
    return this.results.get(resultId);
  }

  /** List all active sessions. */
  listSessions(): ResearchSession[] {
    return Array.from(this.sessions.values()).filter(
      s => s.status === 'running' || s.status === 'pending'
    );
  }

  /** Clean up completed sessions older than 1 hour. */
  cleanup(): void {
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    for (const [id, session] of this.sessions) {
      if (session.status !== 'running' && session.status !== 'pending') {
        const completedAt = new Date(session.updatedAt);
        if (completedAt < oneHourAgo) {
          this.sessions.delete(id);
          this.results.delete(id);
        }
      }
    }
  }

  /**
   * Execute a research task asynchronously.
   * This method runs in the background and updates session progress.
   */
  async executeResearch(sessionId: string, query: ResearchQuery): Promise<ResearchResult> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    // Check concurrent session limit
    const activeSessions = this.listSessions().length;
    if (activeSessions >= this.maxConcurrentSessions && session.status !== 'running') {
      session.status = 'failed';
      session.error = 'Too many concurrent research sessions';
      session.updatedAt = new Date().toISOString();
      throw new Error('Too many concurrent research sessions');
    }

    session.status = 'running';
    session.updatedAt = new Date().toISOString();

    const startTime = Date.now();
    const maxPages = Math.min(query.maxPages || 10, 50);
    const maxDepth = Math.min(query.maxDepth || 2, 5);
    const timeout = query.timeout || 120000;

    const sources: ResearchSource[] = [];
    const visited = new Set<string>();
    const urlsToSearch = query.urls && query.urls.length > 0 ? query.urls : [];

    try {
      // If URLs provided, search those URLs
      if (urlsToSearch.length > 0) {
        for (const url of urlsToSearch) {
          if (session.status !== 'running') break; // Check for cancellation
          if (visited.has(url) || sources.length >= maxPages) break;
          if (!isUrlSafe(url)) continue;

          session.currentUrl = url;
          try {
            const source = await this.researchUrl(url, query, session);
            if (source) {
              sources.push(source);
              visited.add(url);
            }
          } catch {
            // Skip failed pages
          }

          session.pagesVisited = sources.length;
          session.progress = Math.min(Math.round((sources.length / maxPages) * 100), 100);
          session.updatedAt = new Date().toISOString();
        }
      }

      // If we need more pages and have extraction rules, do keyword-based search
      if (sources.length < maxPages && query.extractionRules && query.extractionRules.length > 0) {
        for (const rule of query.extractionRules) {
          if (session.status !== 'running') break;
          if (sources.length >= maxPages) break;

          // Use the search endpoint to find relevant content
          session.progress = Math.min(Math.round((sources.length / maxPages) * 100), 100);
          session.updatedAt = new Date().toISOString();
        }
      }

      const durationMs = Date.now() - startTime;
      const status = sources.length > 0 ? 'completed' : 'partial';

      const result: ResearchResult = {
        id: sessionId,
        query: query.query,
        summary: this.generateSummary(query.query, sources),
        sources,
        pagesVisited: sources.length,
        durationMs,
        status,
        completedAt: new Date().toISOString(),
      };

      this.results.set(sessionId, result);
      session.status = status === 'completed' ? 'completed' : 'completed';
      session.progress = 100;
      session.updatedAt = new Date().toISOString();

      return result;
    } catch (error: any) {
      const durationMs = Date.now() - startTime;
      const errorMessage = error.message || 'Research failed';

      session.status = 'failed';
      session.error = errorMessage;
      session.updatedAt = new Date().toISOString();

      const result: ResearchResult = {
        id: sessionId,
        query: query.query,
        summary: `Research failed: ${errorMessage}`,
        sources,
        pagesVisited: sources.length,
        durationMs,
        status: 'failed',
        error: errorMessage,
        completedAt: new Date().toISOString(),
      };

      this.results.set(sessionId, result);
      return result;
    }
  }

  /** Research a single URL and extract relevant content. */
  private async researchUrl(
    url: string,
    query: ResearchQuery,
    session: ResearchSession
  ): Promise<ResearchSource | null> {
    if (!isUrlSafe(url)) return null;

    let page: BrowserPage | null = null;
    try {
      page = await this.backend.createPage();
      await page.goto(url, { timeout: Math.min(query.timeout || 30000, 60000) });

      const title = await page.title();

      // Extract text content
      const text = await page.evaluate(() => {
        const el = document.body.cloneNode(true) as HTMLElement;
        el.querySelectorAll('script, style, noscript, iframe, nav, footer, header').forEach((e) => e.remove());
        return (el.textContent || '').trim();
      });

      // Calculate relevance based on query terms
      const relevance = this.calculateRelevance(query.query, text);

      await page.close();

      if (relevance < 0.1) {
        return null; // Skip low-relevance pages
      }

      return {
        url,
        title,
        content: text.slice(0, 10000), // Limit content size
        relevance,
        fetchedAt: new Date().toISOString(),
      };
    } catch {
      if (page) {
        try { await page.close(); } catch { /* ignore */ }
      }
      return null;
    }
  }

  /** Calculate relevance score based on query term frequency. */
  private calculateRelevance(query: string, text: string): number {
    const queryTerms = query.toLowerCase().split(/\s+/).filter(t => t.length > 2);
    if (queryTerms.length === 0) return 0.5;

    const textLower = text.toLowerCase();
    let matchCount = 0;
    for (const term of queryTerms) {
      if (textLower.includes(term)) {
        matchCount++;
      }
    }

    return Math.min(matchCount / queryTerms.length, 1.0);
  }

  /** Generate a summary from research sources. */
  private generateSummary(query: string, sources: ResearchSource[]): string {
    if (sources.length === 0) {
      return `No relevant sources found for: ${query}`;
    }

    const topSources = sources
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 5);

    const summaryParts = [
      `Research on "${query}" found ${sources.length} relevant source(s).`,
      '',
      'Top findings:',
    ];

    for (let i = 0; i < topSources.length; i++) {
      const source = topSources[i];
      const preview = source.content.slice(0, 200).replace(/\s+/g, ' ').trim();
      summaryParts.push(`${i + 1}. ${source.title} (${source.url}) - Relevance: ${(source.relevance * 100).toFixed(0)}%`);
      summaryParts.push(`   "${preview}..."`);
    }

    return summaryParts.join('\n');
  }
}
