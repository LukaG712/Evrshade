/** Trapper — Browser backend adapter interface. */

export interface BrowserPage {
  goto(url: string, options?: { timeout?: number }): Promise<void>;
  content(): Promise<string>;
  title(): Promise<string>;
  screenshot(options?: { type?: 'png' | 'jpeg' }): Promise<Buffer>;
  evaluate<T>(pageFunction: string, ...args: unknown[]): Promise<T>;
  fill(selector: string, value: string): Promise<void>;
  click(selector: string): Promise<void>;
  close(): Promise<void>;
}

export interface BrowserBackend {
  /** Initialize the browser backend (launch browser, etc.). */
  initialize(): Promise<void>;

  /** Create a new page for scraping/crawling. */
  createPage(): Promise<BrowserPage>;

  /** Shutdown and release resources. */
  shutdown(): Promise<void>;
}

export type BrowserBackendFactory = () => BrowserBackend;

// ─── Research Task Types ───────────────────────────────────────────────────

export interface ResearchQuery {
  /** Search query or topic to research. */
  query: string;
  /** URLs to search within (optional). */
  urls?: string[];
  /** Maximum number of pages to visit. */
  maxPages?: number;
  /** Maximum depth for crawling. */
  maxDepth?: number;
  /** Specific extraction instructions. */
  extractionRules?: string[];
  /** Timeout in milliseconds. */
  timeout?: number;
}

export interface ResearchSource {
  /** Source URL. */
  url: string;
  /** Page title. */
  title: string;
  /** Extracted text content. */
  content: string;
  /** Relevance score (0-1). */
  relevance: number;
  /** Timestamp when source was fetched. */
  fetchedAt: string;
}

export interface ResearchResult {
  /** Unique result ID. */
  id: string;
  /** Original query. */
  query: string;
  /** Summary of findings. */
  summary: string;
  /** Source pages with extracted content. */
  sources: ResearchSource[];
  /** Total pages visited. */
  pagesVisited: number;
  /** Duration in milliseconds. */
  durationMs: number;
  /** Status of the research task. */
  status: 'completed' | 'partial' | 'failed';
  /** Error message if failed. */
  error?: string;
  /** Timestamp when research completed. */
  completedAt: string;
}

export interface ResearchSession {
  /** Session ID. */
  id: string;
  /** Current status. */
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  /** Progress percentage (0-100). */
  progress: number;
  /** Pages visited so far. */
  pagesVisited: number;
  /** Maximum pages. */
  maxPages: number;
  /** Current URL being processed. */
  currentUrl?: string;
  /** Error message if failed. */
  error?: string;
  /** Created timestamp. */
  createdAt: string;
  /** Last updated timestamp. */
  updatedAt: string;
}
