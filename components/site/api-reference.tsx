import { SERVICES, MISSION_STAGES, VERSION, REPO_URL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const API_ENDPOINTS = [
  { method: 'POST', path: '/api/missions', service: 'Greenie', description: 'Create a new mission with milestones and features' },
  { method: 'GET', path: '/api/missions', service: 'Greenie', description: 'List all missions with pagination' },
  { method: 'GET', path: '/api/missions/{id}', service: 'Greenie', description: 'Get mission details and current state' },
  { method: 'POST', path: '/api/missions/{id}/plan', service: 'Greenie', description: 'Generate LLM-based plan via Shrewd' },
  { method: 'POST', path: '/api/missions/{id}/execute', service: 'Greenie', description: 'Execute mission milestones with parallel workers' },
  { method: 'POST', path: '/api/missions/{id}/validate', service: 'Greenie', description: 'Run test, lint, type and security checks' },
  { method: 'POST', path: '/api/missions/{id}/fix-revalidate', service: 'Greenie', description: 'Auto-fix failures and re-run validation' },
  { method: 'POST', path: '/api/missions/{id}/cancel', service: 'Greenie', description: 'Cancel a running mission' },
  { method: 'POST', path: '/api/missions/{id}/pause', service: 'Greenie', description: 'Pause mission execution' },
  { method: 'POST', path: '/api/missions/{id}/resume', service: 'Greenie', description: 'Resume a paused mission' },
  { method: 'GET', path: '/api/missions/analytics', service: 'Greenie', description: 'Get mission completion analytics' },
  { method: 'GET', path: '/api/missions/{id}/logs', service: 'Greenie', description: 'Stream mission logs via SSE' },
  { method: 'POST', path: '/api/agents', service: 'Greenie', description: 'Create a new agent configuration' },
  { method: 'GET', path: '/api/agents', service: 'Greenie', description: 'List all agents' },
  { method: 'POST', path: '/api/workflows', service: 'Greenie', description: 'Create a workflow with triggers' },
  { method: 'POST', path: '/api/secrets', service: 'Hider', description: 'Store an encrypted secret' },
  { method: 'GET', path: '/api/secrets/{name}', service: 'Hider', description: 'Lease a secret (AES-256-GCM encrypted)' },
  { method: 'POST', path: '/api/notifications', service: 'Poltergeist', description: 'Send notification via configured channel' },
  { method: 'GET', path: '/api/models', service: 'Shrewd', description: 'List available LLM providers' },
  { method: 'POST', path: '/v1/chat/completions', service: 'Shrewd', description: 'OpenAI-compatible chat completions endpoint' },
  { method: 'GET', path: '/api/metrics', service: 'Sneaker', description: 'Get platform metrics and traces' },
  { method: 'POST', path: '/api/alerts', service: 'Sneaker', description: 'Configure alert rules' },
  { method: 'GET', path: '/api/graph/search', service: 'Gobber', description: 'Hybrid search across knowledge graph' },
  { method: 'POST', path: '/api/graph/embed', service: 'Gobber', description: 'Embed and store text chunks' },
  { method: 'POST', path: '/api/crawl', service: 'Trapper', description: 'Start a web crawl with SSRF protection' },
  { method: 'POST', path: '/api/execute', service: 'Slinker', description: 'Execute code in isolated sandbox' },
  { method: 'GET', path: '/api/health', service: 'All', description: 'Health check endpoint for all services' },
]

const methodColor: Record<string, string> = {
  GET: 'text-signal-ink',
  POST: 'text-signal-ink',
}

export function ApiReference() {
  return (
    <section id="api" aria-labelledby="api-title" className="px-4 pt-24 md:px-[max(24px,3vw)] md:pt-40">
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

      <div className="mt-16 border border-foreground md:mt-24">
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
                <tr key={ep.path} className={`border-b border-border ${i % 2 === 0 ? 'bg-muted/30' : ''}`}>
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
        <a href={`${REPO_URL}/tree/main/docs`} target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-signal-ink">
          {REPO_URL}/tree/main/docs
        </a>
      </p>
    </section>
  )
}
