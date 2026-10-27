import { useState, useCallback, useEffect, useRef } from 'react'

// Trapper API URL from environment or relative (for Docker/proxy deployments)
const TRAPPER_URL = ((): string => {
  const envUrl = import.meta.env.VITE_TRAPPER_URL
  if (envUrl) return envUrl
  const baseUrl = import.meta.env.VITE_BASE_URL || ''
  return baseUrl ? `${baseUrl}/trapper` : '/proxy/trapper'
})()

// Types matching Trapper's API schema
interface CrawlOptions {
  url: string
  maxDiscoveryDepth?: number
  limit?: number
  crawlEntireDomain?: boolean
  allowExternalLinks?: boolean
  allowSubdomains?: boolean
  delay?: number
  maxConcurrency?: number
  ignoreRobotsTxt?: boolean
  mobile?: boolean
  scrapeOptions?: {
    formats?: ('markdown' | 'html' | 'links' | 'screenshot' | 'raw')[]
    onlyMainContent?: boolean
    timeout?: number
  }
}

interface CrawlJobStatus {
  success: boolean
  status: 'scraping' | 'completed' | 'failed' | 'cancelled'
  jobId: string
  totalPages: number
  scrapedPages: number
  data?: CrawlResult[]
  errors?: CrawlError[]
  nextPollMs?: number
}

interface CrawlResult {
  success: boolean
  page?: number
  url?: string
  data?: ScrapeData
  error?: string
  metadata?: ScrapeMetadata
}

interface ScrapeData {
  markdown?: string
  html?: string
  links?: string[]
  screenshot?: string
  metadata?: ScrapeMetadata
}

interface ScrapeMetadata {
  title?: string
  description?: string
  language?: string
  sourceURL?: string
  statusCode?: number
  ogTitle?: string
  ogImage?: string
  canonicalUrl?: string
}

interface CrawlError {
  url: string
  error: string
  statusCode?: number
}

function Crawler() {
  // Form state
  const [url, setUrl] = useState('')
  const [maxDepth, setMaxDepth] = useState(3)
  const [maxPages, setMaxPages] = useState(20)
  const [sameDomainOnly, setSameDomainOnly] = useState(true)
  const [includeScreenshots, setIncludeScreenshots] = useState(false)
  const [mobileViewport, setMobileViewport] = useState(false)
  const [ignoreRobots, setIgnoreRobots] = useState(false)

  // Job state
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<CrawlJobStatus | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [urlError, setUrlError] = useState<string | null>(null)

  // Results view state
  const [selectedPage, setSelectedPage] = useState<CrawlResult | null>(null)
  const [searchFilter, setSearchFilter] = useState('')
  const [sortBy, setSortBy] = useState<'url' | 'status' | 'page'>('page')

  // Polling ref
  const pollIntervalRef = useRef<number | null>(null)
  const isCancelledRef = useRef(false)

  // Validate URL format
  const validateUrl = useCallback((value: string): string | null => {
    if (!value.trim()) return 'URL is required'
    try {
      const parsed = new URL(value)
      if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
        return 'URL must use http:// or https://'
      }
      return null
    } catch {
      return 'Invalid URL format (e.g., https://example.com)'
    }
  }, [])

  // Handle URL input change
  const handleUrlChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setUrl(value)
    setUrlError(null)
    if (value) {
      setUrlError(validateUrl(value))
    }
  }, [validateUrl])

  // Start a crawl job
  const startCrawl = useCallback(async () => {
    const validationError = validateUrl(url)
    if (validationError) {
      setUrlError(validationError)
      return
    }

    setIsRunning(true)
    setError(null)
    isCancelledRef.current = false

    const options: CrawlOptions = {
      url,
      maxDiscoveryDepth: maxDepth,
      limit: maxPages,
      crawlEntireDomain: !sameDomainOnly,
      allowExternalLinks: !sameDomainOnly,
      allowSubdomains: true,
      ignoreRobotsTxt: ignoreRobots,
      mobile: mobileViewport,
      scrapeOptions: {
        formats: includeScreenshots ? ['markdown', 'screenshot'] : ['markdown'],
        onlyMainContent: true,
      },
    }

    try {
      const resp = await fetch(`${TRAPPER_URL}/crawl`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(options),
        signal: AbortSignal.timeout(10000),
      })

      if (!resp.ok) {
        const errData = await resp.json().catch(() => ({}))
        throw new Error(errData.error || `Trapper returned ${resp.status}`)
      }

      const data = await resp.json()
      if (!data.success || !data.jobId) {
        throw new Error(data.error || 'No job ID returned')
      }

      setCurrentJobId(data.jobId)
      setJobStatus(null)
      setSelectedPage(null)

      // Start polling
      const poll = async () => {
        if (isCancelledRef.current) return
        try {
          const statusResp = await fetch(`${TRAPPER_URL}/crawl/${data.jobId}`, {
            signal: AbortSignal.timeout(10000),
          })
          if (!statusResp.ok) return

          const statusData = await statusResp.json()
          if (statusData.success) {
            const status: CrawlJobStatus = {
              success: true,
              status: statusData.status,
              jobId: statusData.jobId,
              totalPages: statusData.totalPages || 0,
              scrapedPages: statusData.scrapedPages || 0,
              data: statusData.data || [],
              errors: statusData.errors || [],
              nextPollMs: statusData.nextPollMs,
            }
            setJobStatus(status)

            // Stop polling on terminal states
            if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
              setIsRunning(false)
              if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current)
                pollIntervalRef.current = null
              }
            }
          }
        } catch {
          // Network error during polling — continue trying
        }
      }

      // Poll immediately, then at interval
      await poll()
      if (!isCancelledRef.current) {
        pollIntervalRef.current = window.setInterval(poll, 2000)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start crawl')
      setIsRunning(false)
    }
  }, [url, maxDepth, maxPages, sameDomainOnly, includeScreenshots, ignoreRobots, mobileViewport, validateUrl])

  // Cancel crawl
  const cancelCrawl = useCallback(async () => {
    if (!currentJobId) return
    isCancelledRef.current = true

    try {
      await fetch(`${TRAPPER_URL}/crawl/${currentJobId}`, {
        method: 'DELETE',
        signal: AbortSignal.timeout(5000),
      })
    } catch {
      // Ignore errors during cancel
    }

    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current)
      pollIntervalRef.current = null
    }
    setIsRunning(false)
    setJobStatus(prev => prev ? { ...prev, status: 'cancelled' } : null)
  }, [currentJobId])

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
      }
    }
  }, [])

  // Filter and sort results
  const filteredResults = useCallback(() => {
    if (!jobStatus?.data) return []
    let results = [...jobStatus.data]

    if (searchFilter) {
      const filter = searchFilter.toLowerCase()
      results = results.filter(r =>
        r.url?.toLowerCase().includes(filter) ||
        r.data?.metadata?.title?.toLowerCase().includes(filter) ||
        r.error?.toLowerCase().includes(filter)
      )
    }

    results.sort((a, b) => {
      if (sortBy === 'page') return (a.page || 0) - (b.page || 0)
      if (sortBy === 'status') return (a.success ? 0 : 1) - (b.success ? 0 : 1)
      return (a.url || '').localeCompare(b.url || '')
    })

    return results
  }, [jobStatus?.data, searchFilter, sortBy])

  // Export results as JSON
  const exportJson = useCallback(() => {
    if (!jobStatus?.data) return
    const blob = new Blob([JSON.stringify(filteredResults(), null, 2)], { type: 'application/json' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `crawl-${currentJobId?.slice(0, 8)}.json`
    link.click()
    URL.revokeObjectURL(link.href)
  }, [jobStatus, currentJobId, filteredResults])

  // Export results as CSV
  const exportCsv = useCallback(() => {
    if (!jobStatus?.data) return
    const rows = [['URL', 'Title', 'Status', 'Error']]
    for (const r of filteredResults()) {
      rows.push([
        r.url || '',
        r.data?.metadata?.title || '',
        r.success ? 'Success' : 'Failed',
        r.error || '',
      ].map(v => `"${String(v).replace(/"/g, '""')}"`))
    }
    const blob = new Blob([rows.map(r => r.join(',')).join('\n')], { type: 'text/csv' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `crawl-${currentJobId?.slice(0, 8)}.csv`
    link.click()
    URL.revokeObjectURL(link.href)
  }, [jobStatus, currentJobId, filteredResults])

  // Reset form
  const resetForm = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current)
      pollIntervalRef.current = null
    }
    isCancelledRef.current = false
    setCurrentJobId(null)
    setJobStatus(null)
    setIsRunning(false)
    setError(null)
    setSelectedPage(null)
    setSearchFilter('')
  }, [])

  const hasResults = jobStatus?.data && jobStatus.data.length > 0
  const successCount = jobStatus?.data?.filter(r => r.success).length || 0
  const errorCount = jobStatus?.errors?.length || 0

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">🕷️ Web Crawler</h2>
        {jobStatus && (
          <button onClick={resetForm} className="px-3 py-1 text-sm bg-gray-700 rounded hover:bg-gray-600">
            New Crawl
          </button>
        )}
      </div>

      {/* Crawl Form */}
      {!jobStatus && !isRunning && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Target URL *
            </label>
            <input
              type="url"
              value={url}
              onChange={handleUrlChange}
              placeholder="https://example.com"
              className="w-full px-3 py-2 bg-gray-900 border border-gray-600 rounded text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
            {urlError && <p className="mt-1 text-sm text-red-400">{urlError}</p>}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Max Depth: {maxDepth}
              </label>
              <input
                type="range"
                min="0"
                max="10"
                value={maxDepth}
                onChange={e => setMaxDepth(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Max Pages: {maxPages}
              </label>
              <input
                type="range"
                min="1"
                max="100"
                value={maxPages}
                onChange={e => setMaxPages(Number(e.target.value))}
                className="w-full"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="sameDomain"
                checked={sameDomainOnly}
                onChange={e => setSameDomainOnly(e.target.checked)}
                className="rounded bg-gray-900 border-gray-600"
              />
              <label htmlFor="sameDomain" className="text-sm text-gray-300">
                Same domain only
              </label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="screenshots"
                checked={includeScreenshots}
                onChange={e => setIncludeScreenshots(e.target.checked)}
                className="rounded bg-gray-900 border-gray-600"
              />
              <label htmlFor="screenshots" className="text-sm text-gray-300">
                Include screenshots
              </label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="mobile"
                checked={mobileViewport}
                onChange={e => setMobileViewport(e.target.checked)}
                className="rounded bg-gray-900 border-gray-600"
              />
              <label htmlFor="mobile" className="text-sm text-gray-300">
                Mobile viewport
              </label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="ignoreRobots"
                checked={ignoreRobots}
                onChange={e => setIgnoreRobots(e.target.checked)}
                className="rounded bg-gray-900 border-gray-600"
              />
              <label htmlFor="ignoreRobots" className="text-sm text-gray-300">
                Ignore robots.txt
              </label>
            </div>
          </div>

          {error && (
            <div className="bg-red-900/30 border border-red-700 rounded p-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            onClick={startCrawl}
            disabled={!!urlError || !url.trim()}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed"
          >
            Start Crawl
          </button>
        </div>
      )}

      {/* Running State */}
      {isRunning && jobStatus && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="font-semibold text-lg">Crawl in progress</h3>
              <p className="text-sm text-gray-400">Job: {currentJobId?.slice(0, 12)}</p>
            </div>
            <button
              onClick={cancelCrawl}
              className="px-3 py-1 text-sm bg-red-600 rounded hover:bg-red-700"
            >
              Cancel
            </button>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Progress</span>
              <span className="text-white">
                {jobStatus.scrapedPages} / {jobStatus.totalPages} pages
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all"
                style={{
                  width: jobStatus.totalPages
                    ? `${(jobStatus.scrapedPages / jobStatus.totalPages) * 100}%`
                    : '0%',
                }}
              />
            </div>
          </div>

          {jobStatus.errors && jobStatus.errors.length > 0 && (
            <p className="text-sm text-yellow-400">
              {jobStatus.errors.length} error{jobStatus.errors.length > 1 ? 's' : ''} so far
            </p>
          )}

          {/* Live results while running */}
          {hasResults && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-300">Pages crawled so far</h4>
              <div className="max-h-60 overflow-y-auto space-y-1">
                {filteredResults().slice(0, 20).map((r, i) => (
                  <div
                    key={i}
                    className={`flex items-center gap-2 px-3 py-2 rounded text-sm ${
                      r.success ? 'bg-green-900/20' : 'bg-red-900/20'
                    }`}
                  >
                    <span className={r.success ? 'text-green-400' : 'text-red-400'}>
                      {r.success ? '✓' : '✗'}
                    </span>
                    <span className="text-gray-300 truncate flex-1">{r.url || 'Unknown'}</span>
                    {r.error && <span className="text-red-400 text-xs truncate max-w-48">{r.error}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Completed / Failed State */}
      {jobStatus && !isRunning && (
        <div className="space-y-4">
          {/* Summary */}
          <div className={`rounded-lg p-4 border ${
            jobStatus.status === 'completed'
              ? 'bg-green-900/20 border-green-700'
              : jobStatus.status === 'cancelled'
              ? 'bg-yellow-900/20 border-yellow-700'
              : 'bg-red-900/20 border-red-700'
          }`}>
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-lg">
                  {jobStatus.status === 'completed' ? '✓ Crawl Completed' :
                   jobStatus.status === 'cancelled' ? '⏹ Crawl Cancelled' :
                   '✗ Crawl Failed'}
                </h3>
                <p className="text-sm text-gray-400 mt-1">
                  {successCount} page{successCount !== 1 ? 's' : ''} crawled
                  {errorCount > 0 && `, ${errorCount} error${errorCount > 1 ? 's' : ''}`}
                </p>
              </div>
              <div className="flex gap-2">
                {hasResults && (
                  <>
                    <button onClick={exportJson} className="px-3 py-1 text-sm bg-gray-700 rounded hover:bg-gray-600">
                      Export JSON
                    </button>
                    <button onClick={exportCsv} className="px-3 py-1 text-sm bg-gray-700 rounded hover:bg-gray-600">
                      Export CSV
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Search and filter */}
          {hasResults && (
            <div className="flex gap-2">
              <input
                type="text"
                value={searchFilter}
                onChange={e => setSearchFilter(e.target.value)}
                placeholder="Search results..."
                className="flex-1 px-3 py-2 bg-gray-900 border border-gray-600 rounded text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
              <select
                value={sortBy}
                onChange={e => setSortBy(e.target.value as 'url' | 'status' | 'page')}
                className="px-3 py-2 bg-gray-900 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
              >
                <option value="page">Sort by page</option>
                <option value="url">Sort by URL</option>
                <option value="status">Sort by status</option>
              </select>
            </div>
          )}

          {/* Selected page detail */}
          {selectedPage && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{selectedPage.data?.metadata?.title || 'Untitled'}</h3>
                  <p className="text-sm text-gray-400 break-all">{selectedPage.url}</p>
                </div>
                <button
                  onClick={() => setSelectedPage(null)}
                  className="px-2 py-1 text-sm bg-gray-700 rounded hover:bg-gray-600"
                >
                  Close
                </button>
              </div>

              {selectedPage.data?.metadata && (
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {selectedPage.data.metadata.description && (
                    <p><span className="text-gray-400">Description:</span> {selectedPage.data.metadata.description}</p>
                  )}
                  {selectedPage.data.metadata.language && (
                    <p><span className="text-gray-400">Language:</span> {selectedPage.data.metadata.language}</p>
                  )}
                  {selectedPage.data.metadata.statusCode && (
                    <p><span className="text-gray-400">Status:</span> {selectedPage.data.metadata.statusCode}</p>
                  )}
                  {selectedPage.data.metadata.ogImage && (
                    <p><span className="text-gray-400">OG Image:</span> {selectedPage.data.metadata.ogImage}</p>
                  )}
                </div>
              )}

              {selectedPage.data?.markdown && (
                <div>
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Content (Markdown)</h4>
                  <pre className="bg-gray-900 p-4 rounded text-sm text-gray-300 max-h-96 overflow-auto whitespace-pre-wrap">
                    {selectedPage.data.markdown.slice(0, 5000)}
                    {selectedPage.data.markdown.length > 5000 && '\n... (truncated)'}
                  </pre>
                </div>
              )}

              {selectedPage.data?.screenshot && (
                <div>
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Screenshot</h4>
                  <img
                    src={`data:image/png;base64,${selectedPage.data.screenshot}`}
                    alt="Page screenshot"
                    className="max-w-full rounded border border-gray-700"
                  />
                </div>
              )}

              {selectedPage.error && (
                <div className="bg-red-900/30 border border-red-700 rounded p-3 text-sm text-red-400">
                  Error: {selectedPage.error}
                </div>
              )}
            </div>
          )}

          {/* Results list */}
          {hasResults && !selectedPage && (
            <div className="bg-gray-800 rounded-lg border border-gray-700 divide-y divide-gray-700">
              {filteredResults().map((r, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedPage(r)}
                  className="w-full text-left px-4 py-3 hover:bg-gray-700/50 flex items-start gap-3"
                >
                  <span className={`mt-0.5 ${r.success ? 'text-green-400' : 'text-red-400'}`}>
                    {r.success ? '✓' : '✗'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white truncate">
                      {r.data?.metadata?.title || r.url || 'Unknown'}
                    </p>
                    <p className="text-xs text-gray-400 truncate">{r.url}</p>
                    {r.error && <p className="text-xs text-red-400 mt-1">{r.error}</p>}
                  </div>
                  <span className="text-xs text-gray-500">Page {r.page}</span>
                </button>
              ))}
            </div>
          )}

          {/* Errors summary */}
          {jobStatus.errors && jobStatus.errors.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h4 className="text-sm font-medium text-yellow-400 mb-2">
                Errors ({jobStatus.errors.length})
              </h4>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {jobStatus.errors.map((err, i) => (
                  <div key={i} className="text-sm">
                    <span className="text-gray-400 truncate">{err.url}</span>
                    <span className="text-red-400 ml-2">{err.error}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty state */}
          {!hasResults && jobStatus.status === 'completed' && (
            <div className="bg-gray-800 rounded-lg p-8 border border-gray-700 text-center">
              <p className="text-gray-400">No pages were crawled. The target site may be empty or blocked.</p>
            </div>
          )}
        </div>
      )}

      {/* Empty state - no job started */}
      {!jobStatus && !isRunning && (
        <div className="bg-gray-800/50 rounded-lg p-8 border border-gray-700 text-center">
          <p className="text-gray-500">Enter a URL above to start crawling.</p>
        </div>
      )}
    </div>
  )
}

export default Crawler
