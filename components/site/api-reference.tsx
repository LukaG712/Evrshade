'use client'

import { ChevronDown } from 'lucide-react'
import { SERVICES, MISSION_STAGES, VERSION, REPO_URL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const API_ENDPOINTS = [
  { method: 'GET', path: '/api/health', service: 'Greenie', description: 'Health check' },
  { method: 'GET', path: '/api/ready', service: 'Greenie', description: 'Readiness check' },
  { method: 'GET', path: '/api/status', service: 'Greenie', description: 'Agent and service status' },
  { method: 'GET', path: '/api/agents', service: 'Greenie', description: 'List agents' },
  { method: 'POST', path: '/api/agents', service: 'Greenie', description: 'Create agent' },
  { method: 'GET', path: '/api/sessions', service: 'Greenie', description: 'List sessions' },
  { method: 'POST', path: '/api/chat', service: 'Greenie', description: 'Send chat message' },
  { method: 'GET', path: '/api/workflows', service: 'Greenie', description: 'List workflows' },
  { method: 'POST', path: '/api/workflows', service: 'Greenie', description: 'Create workflow' },
  { method: 'GET', path: '/api/workstations', service: 'Greenie', description: 'List workstations' },
  { method: 'POST', path: '/api/workstations', service: 'Greenie', description: 'Create workstation' },
  { method: 'GET', path: '/api/mcp/servers', service: 'Greenie', description: 'List MCP servers' },
  { method: 'POST', path: '/api/mcp/servers', service: 'Greenie', description: 'Add MCP server' },
  { method: 'GET', path: '/api/plugins', service: 'Greenie', description: 'List plugins' },
  { method: 'POST', path: '/api/plugins', service: 'Greenie', description: 'Install plugin' },
  { method: 'GET', path: '/api/system/stats', service: 'Greenie', description: 'System resource stats' },
  { method: 'GET', path: '/api/system/logs', service: 'Greenie', description: 'Aggregated logs' },
  { method: 'POST', path: '/api/emergency/stop', service: 'Greenie', description: 'Activate emergency stop' },
  { method: 'POST', path: '/api/emergency/resume', service: 'Greenie', description: 'Resume after emergency stop' },
  { method: 'GET', path: '/api/timeline/events', service: 'Greenie', description: 'Query activity timeline' },
  { method: 'GET', path: '/api/audit/events', service: 'Greenie', description: 'Security audit trail' },
  { method: 'POST', path: '/api/credentials/rotate', service: 'Greenie', description: 'Rotate credential' },
  { method: 'GET', path: '/api/backup', service: 'Greenie', description: 'List backups' },
  { method: 'POST', path: '/api/backup', service: 'Greenie', description: 'Create backup' },
  { method: 'GET', path: '/docs', service: 'Greenie', description: 'Swagger UI' },
  { method: 'GET', path: '/api/v1/tasks', service: 'Slinker', description: 'List tasks' },
  { method: 'GET', path: '/api/v1/tasks/{id}', service: 'Slinker', description: 'Get task details' },
  { method: 'GET', path: '/api/v1/workers', service: 'Slinker', description: 'List workers' },
  { method: 'GET', path: '/api/v1/projects', service: 'Slinker', description: 'List projects' },
  { method: 'POST', path: '/api/v1/projects', service: 'Slinker', description: 'Register project' },
  { method: 'POST', path: '/v1/chat/completions', service: 'Slinker', description: 'OpenAI-compatible chat' },
  { method: 'POST', path: '/api/scrape', service: 'Trapper', description: 'Scrape a single page' },
  { method: 'POST', path: '/api/crawl', service: 'Trapper', description: 'Start a crawl job' },
  { method: 'POST', path: '/api/search', service: 'Trapper', description: 'Search the web' },
  { method: 'POST', path: '/api/extract', service: 'Trapper', description: 'Extract structured data' },
  { method: 'POST', path: '/api/agent', service: 'Trapper', description: 'Autonomous browsing agent' },
  { method: 'POST', path: '/api/vault/index', service: 'Gobber', description: 'Index Obsidian vault' },
  { method: 'POST', path: '/api/vault/search', service: 'Gobber', description: 'Semantic search' },
  { method: 'GET', path: '/api/vault/notes', service: 'Gobber', description: 'List notes' },
  { method: 'POST', path: '/api/cache', service: 'Gobber', description: 'Set cache entry' },
  { method: 'POST', path: '/api/metrics', service: 'Sneaker', description: 'Record metric' },
  { method: 'GET', path: '/api/metrics', service: 'Sneaker', description: 'Query metrics' },
  { method: 'POST', path: '/api/traces', service: 'Sneaker', description: 'Record trace span' },
  { method: 'POST', path: '/api/logs', service: 'Sneaker', description: 'Record log entry' },
  { method: 'GET', path: '/api/alerts', service: 'Sneaker', description: 'List fired alerts' },
  { method: 'GET', path: '/api/alerts/rules', service: 'Sneaker', description: 'List alert rules' },
  { method: 'POST', path: '/api/secrets', service: 'Hider', description: 'Create secret' },
  { method: 'GET', path: '/api/secrets', service: 'Hider', description: 'List secrets' },
  { method: 'GET', path: '/api/secrets/{key}', service: 'Hider', description: 'Get secret' },
  { method: 'POST', path: '/api/configs', service: 'Hider', description: 'Create config' },
  { method: 'POST', path: '/api/notifications', service: 'Poltergeist', description: 'Send notification' },
  { method: 'GET', path: '/api/notifications', service: 'Poltergeist', description: 'List notifications' },
  { method: 'POST', path: '/api/templates', service: 'Poltergeist', description: 'Create template' },
  { method: 'POST', path: '/api/chat', service: 'Shrewd', description: 'Chat completion' },
  { method: 'GET', path: '/api/models', service: 'Shrewd', description: 'List available models' },
  { method: 'GET', path: '/api/providers', service: 'Shrewd', description: 'List providers' },
]

const methodColor: Record<string, string> = {
  GET: 'text-signal-ink',
  POST: 'text-signal-ink',
}

export function ApiReference() {
  return (
    <section id="api" aria-labelledby="api-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="api-title"
        label="API Reference"
        title={
          <>
            Every service,
            <br />
            <span className="text-muted-foreground">one interface.</span>
          </>
        }
        lead={`All ${SERVICES.length} services expose a REST API. Below are the core endpoints across the platform. Full OpenAPI specs are available in the repository.`}
      />

      <details className="mt-16 group/details md:mt-24">
        <summary className="mb-4 flex cursor-pointer items-center justify-between font-mono text-[11px] uppercase tracking-wider text-signal-ink">
          {'API endpoints'}
          <ChevronDown className="size-4 transition-transform group-open/details:rotate-180" aria-hidden="true" />
        </summary>
        <div className="border border-foreground">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-foreground">
                  <th className="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-wider text-muted-foreground">Method</th>
                  <th className="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-wider text-muted-foreground">Endpoint</th>
                  <th className="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-wider text-muted-foreground hidden sm:table-cell">Service</th>
                  <th className="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-wider text-muted-foreground hidden md:table-cell">Description</th>
                </tr>
              </thead>
              <tbody>
                {API_ENDPOINTS.map((ep, i) => (
                  <tr key={i} className={`border-b border-border ${i % 2 === 0 ? 'bg-muted/30' : ''}`}>
                    <td className={`px-4 py-3 font-mono text-[11px] font-bold uppercase ${methodColor[ep.method] || ''}`}>{ep.method}</td>
                    <td className="px-4 py-3 font-mono text-[13px]">{ep.path}</td>
                    <td className="px-4 py-3 text-muted-foreground hidden sm:table-cell">{ep.service}</td>
                    <td className="px-4 py-3 text-muted-foreground hidden md:table-cell">{ep.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </details>

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <div className="border border-foreground p-5">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Base URL'}</p>
          <code className="mt-3 block font-mono text-sm text-muted-foreground">http://localhost:8080</code>
          <p className="mt-2 text-xs text-muted-foreground">All services are accessible through Greenie on port 8080. Direct service ports are available for debugging.</p>
        </div>
        <div className="border border-foreground p-5">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Authentication'}</p>
          <code className="mt-3 block font-mono text-sm text-muted-foreground">Authorization: Bearer &lt;token&gt;</code>
          <p className="mt-2 text-xs text-muted-foreground">Bearer token auth is required on all endpoints. Tokens are managed by Hider with AES-256-GCM encryption.</p>
        </div>
      </div>

      <p className="mt-6 text-xs text-muted-foreground">
        Full API documentation →{' '}
        <a href={`${REPO_URL}/tree/master/docs`} target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-signal-ink">
          {REPO_URL}/tree/master/docs
        </a>
      </p>
    </section>
  )
}
