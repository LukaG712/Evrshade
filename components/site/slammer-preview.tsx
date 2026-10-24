import { Activity, CheckCircle, Clock, AlertTriangle, Terminal, BarChart3, Shield, Play, Pause } from 'lucide-react'
import { SectionHeading } from './section-heading'

const DASHBOARD_PANELS = [
  {
    title: 'Missions',
    icon: Activity,
    rows: [
      { name: 'm_7f3a · Add rate limiting', status: 'running', progress: 67 },
      { name: 'm_2e91 · Update dependencies', status: 'queued', progress: 0 },
      { name: 'm_4b1c · Refactor auth module', status: 'completed', progress: 100 },
      { name: 'm_8d5f · Fix login timeout', status: 'failed', progress: 42 },
    ],
  },
  {
    title: 'Agents',
    icon: Terminal,
    rows: [
      { name: 'worker-1 · m_7f3a', status: 'running', progress: 0 },
      { name: 'worker-2 · idle', status: 'queued', progress: 0 },
      { name: 'worker-3 · idle', status: 'queued', progress: 0 },
    ],
  },
  {
    title: 'Approvals',
    icon: Shield,
    rows: [
      { name: 'Install express@5.0', status: 'running', progress: 0 },
      { name: 'Push to main branch', status: 'queued', progress: 0 },
    ],
  },
] as const

function statusColor(status: string) {
  switch (status) {
    case 'running':
      return 'text-signal'
    case 'completed':
      return 'text-muted-foreground'
    case 'failed':
      return 'text-destructive'
    default:
      return 'text-muted-foreground/60'
  }
}

function statusIcon(status: string) {
  switch (status) {
    case 'running':
      return <Play className="size-3" aria-hidden="true" />
    case 'completed':
      return <CheckCircle className="size-3" aria-hidden="true" />
    case 'failed':
      return <AlertTriangle className="size-3" aria-hidden="true" />
    default:
      return <Clock className="size-3" aria-hidden="true" />
  }
}

export function SlammerPreview() {
  return (
    <section id="slammer" aria-labelledby="slammer-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="slammer-title"
        label="Slammer"
        title={
          <>
            See everything.
            <br />
            <span className="text-muted-foreground">Control everything.</span>
          </>
        }
        lead="Slammer is the React web dashboard. Monitor missions, approve sensitive operations, watch agents work, and review logs — all from a single interface."
      />

      {/* Dashboard mockup */}
      <div className="mt-12 md:mt-24">
        <div className="overflow-hidden rounded-lg border border-border bg-background">
          {/* Title bar */}
          <div className="flex items-center gap-2 border-b border-border bg-foreground/[0.03] px-4 py-3">
            <div className="flex gap-1.5">
              <span className="size-2.5 rounded-full border border-foreground/30" />
              <span className="size-2.5 rounded-full border border-foreground/30" />
              <span className="size-2.5 rounded-full border border-foreground/30" />
            </div>
            <span className="ml-3 font-mono text-[11px] text-muted-foreground">Slammer — Evershade Dashboard</span>
          </div>

          {/* Top bar */}
          <div className="flex items-center justify-between border-b border-border px-6 py-3">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-2 font-mono text-[11px] text-signal">
                <span className="size-2 animate-pulse rounded-full bg-signal" aria-hidden="true" />
                Live
              </span>
              <span className="font-mono text-[11px] text-muted-foreground">3 services active</span>
            </div>
            <div className="flex items-center gap-2">
              <button className="flex items-center gap-1.5 rounded border border-border px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider hover:bg-foreground hover:text-background">
                <Play className="size-3" aria-hidden="true" />
                New mission
              </button>
              <button className="flex items-center gap-1.5 rounded border border-border px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider hover:bg-foreground hover:text-background">
                <Pause className="size-3" aria-hidden="true" />
                Pause all
              </button>
            </div>
          </div>

          {/* Stats bar */}
          <div className="grid grid-cols-4 gap-px border-b border-border bg-border">
            {[
              { label: 'Active missions', value: '1', icon: Activity },
              { label: 'Workers', value: '1/3', icon: Terminal },
              { label: 'Pending approvals', value: '2', icon: Shield },
              { label: 'Model cost today', value: '$0.04', icon: BarChart3 },
            ].map((stat) => {
              const Icon = stat.icon
              return (
                <div key={stat.label} className="flex items-center gap-3 bg-background px-6 py-4">
                  <Icon className="size-4 text-muted-foreground/60" aria-hidden="true" />
                  <div>
                    <p className="text-xl font-semibold tracking-tight">{stat.value}</p>
                    <p className="font-mono text-[10px] text-muted-foreground">{stat.label}</p>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Panels grid */}
          <div className="grid grid-cols-1 gap-px bg-border md:grid-cols-3">
            {DASHBOARD_PANELS.map((panel) => {
              const PanelIcon = panel.icon
              return (
                <div key={panel.title} className="bg-background">
                  <div className="flex items-center justify-between border-b border-border px-5 py-3">
                    <div className="flex items-center gap-2">
                      <PanelIcon className="size-4 text-muted-foreground/60" aria-hidden="true" />
                      <span className="font-mono text-[11px] uppercase tracking-wider">{panel.title}</span>
                    </div>
                    <span className="font-mono text-[10px] text-muted-foreground">{panel.rows.length} items</span>
                  </div>
                  <div className="divide-y divide-border">
                    {panel.rows.map((row) => (
                      <div key={row.name} className="flex items-center justify-between px-5 py-3">
                        <div className="flex items-center gap-2">
                          <span className={`flex items-center gap-1.5 font-mono text-[11px] ${statusColor(row.status)}`}>
                            {statusIcon(row.status)}
                            {row.name}
                          </span>
                        </div>
                        {row.progress > 0 && row.progress < 100 && (
                          <div className="flex items-center gap-2">
                            <div className="h-1.5 w-16 overflow-hidden rounded-full bg-border">
                              <div
                                className={`h-full rounded-full ${row.status === 'failed' ? 'bg-destructive' : 'bg-signal'}`}
                                style={{ width: `${row.progress}%` }}
                              />
                            </div>
                            <span className="font-mono text-[10px] text-muted-foreground">{row.progress}%</span>
                          </div>
                        )}
                        {row.status === 'completed' && (
                          <span className="font-mono text-[10px] text-muted-foreground">Done</span>
                        )}
                        {row.status === 'queued' && (
                          <span className="font-mono text-[10px] text-muted-foreground/60">Waiting</span>
                        )}
                        {row.status === 'failed' && (
                          <span className="font-mono text-[10px] text-destructive">Failed</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Bottom log area */}
          <div className="border-t border-border">
            <div className="flex items-center justify-between border-b border-border px-5 py-2">
              <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Live logs</span>
              <span className="font-mono text-[10px] text-muted-foreground/60">SSE stream</span>
            </div>
            <div className="max-h-32 overflow-hidden bg-foreground/[0.02] p-4 font-mono text-[10px] leading-relaxed text-muted-foreground">
              <p><span className="text-muted-foreground/40">14:07:23</span> <span className="text-signal">greenie</span> mission m_7f3a · milestone 2/3 · feature "add middleware" started</p>
              <p><span className="text-muted-foreground/40">14:07:24</span> <span className="text-signal">slinker</span> worker-1 · container created · alpine:3.20</p>
              <p><span className="text-muted-foreground/40">14:07:25</span> <span className="text-signal">shrewd</span> route → planner model · cost $0.0012</p>
              <p><span className="text-muted-foreground/40">14:07:28</span> <span className="text-signal">slinker</span> worker-1 · pytest -q · 12 passed in 2.4s</p>
              <p><span className="text-muted-foreground/40">14:07:30</span> <span className="text-signal">hider</span> lease GITHUB_TOKEN · aes-256-gcm · ok</p>
            </div>
          </div>
        </div>

        <p className="mt-4 font-mono text-[10px] text-muted-foreground">{'Slammer runs on port 5173. Accessible via browser or reverse proxy. SSE streaming for real-time updates.'}</p>
      </div>

      {/* Features list */}
      <div className="mt-12 grid gap-4 md:mt-16 md:grid-cols-3">
        {[
          {
            title: 'Mission overview',
            body: 'See every mission\'s status, progress, and timeline at a glance. Filter by status, search by name, and drill into details.',
          },
          {
            title: 'Approval queue',
            body: 'Sensitive operations wait here. Review the concrete action — not model-written justification — and approve or deny with one click.',
          },
          {
            title: 'Live logs',
            body: 'Server-Sent Events stream logs from all services in real time. Secret redaction is applied automatically.',
          },
        ].map((feature) => (
          <div key={feature.title} className="border-t border-foreground pt-6">
            <h3 className="text-lg font-semibold tracking-tight">{feature.title}</h3>
            <p className="mt-2 text-sm leading-snug text-muted-foreground">{feature.body}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
