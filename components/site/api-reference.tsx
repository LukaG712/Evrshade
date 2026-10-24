'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { SERVICES, REPO_URL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const API_ENDPOINTS = [
  { method: 'POST', path: '/api/missions', service: 'Greenie', description: 'Create a new mission with milestones' },
  { method: 'GET', path: '/api/missions/{id}', service: 'Greenie', description: 'Get mission details and current state' },
  { method: 'POST', path: '/api/missions/{id}/execute', service: 'Greenie', description: 'Execute mission milestones' },
  { method: 'POST', path: '/api/missions/{id}/validate', service: 'Greenie', description: 'Run tests, lint, and security checks' },
  { method: 'GET', path: '/api/missions/{id}/logs', service: 'Greenie', description: 'Stream mission logs via SSE' },
  { method: 'POST', path: '/api/secrets', service: 'Hider', description: 'Store an encrypted secret' },
  { method: 'POST', path: '/api/notifications', service: 'Poltergeist', description: 'Send notification via configured channel' },
  { method: 'POST', path: '/v1/chat/completions', service: 'Shrewd', description: 'OpenAI-compatible chat completions' },
  { method: 'GET', path: '/api/metrics', service: 'Sneaker', description: 'Get platform metrics and traces' },
  { method: 'GET', path: '/api/graph/search', service: 'Gobber', description: 'Hybrid search across knowledge graph' },
  { method: 'POST', path: '/api/execute', service: 'Slinker', description: 'Execute code in isolated sandbox' },
  { method: 'GET', path: '/api/health', service: 'All', description: 'Health check for all services' },
]

const methodColor: Record<string, string> = {
  GET: 'text-signal-ink',
  POST: 'text-signal-ink',
}

// Group endpoints by service for mobile accordion
const groupedEndpoints = API_ENDPOINTS.reduce((acc, ep) => {
  const service = ep.service === 'All' ? 'Platform' : ep.service
  if (!acc[service]) acc[service] = []
  acc[service].push(ep)
  return acc
}, {} as Record<string, typeof API_ENDPOINTS>)

export function ApiReference() {
  const [openService, setOpenService] = useState<string | null>(null)

  return (
    <section id="api" aria-labelledby="api-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
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

      {/* Mobile: accordion by service */}
      <div className="mt-12 space-y-2 md:hidden">
        {Object.entries(groupedEndpoints).map(([service, endpoints]) => (
          <div key={service} className="border border-border">
            <button
              onClick={() => setOpenService(openService === service ? null : service)}
              className="flex w-full items-center justify-between p-4 text-left"
              aria-expanded={openService === service}
            >
              <div>
                <p className="font-semibold tracking-tight">{service}</p>
                <p className="text-xs text-muted-foreground">{endpoints.length} endpoints</p>
              </div>
              {openService === service ? (
                <ChevronUp className="size-4 text-muted-foreground" aria-hidden="true" />
              ) : (
                <ChevronDown className="size-4 text-muted-foreground" aria-hidden="true" />
              )}
            </button>
            {openService === service && (
              <div className="border-t border-border px-4 pb-4">
                <div className="mt-3 space-y-2">
                  {endpoints.map((ep) => (
                    <div key={ep.path} className="rounded border border-border p-3">
                      <div className="flex items-start gap-2">
                        <span className={`font-mono text-[11px] font-bold uppercase ${methodColor[ep.method] || ''}`}>{ep.method}</span>
                        <code className="font-mono text-xs">{ep.path}</code>
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">{ep.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Desktop: full table */}
      <div className="hidden mt-16 border border-foreground md:block md:mt-24">
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
        <a href={`${REPO_URL}/tree/master/docs`} target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-signal-ink">
          {REPO_URL}/tree/master/docs
        </a>
      </p>
    </section>
  )
}
