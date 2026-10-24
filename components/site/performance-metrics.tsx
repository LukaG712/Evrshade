import { Box, Cpu, Layers, Lock, Server, Terminal, Zap } from 'lucide-react'
import { SectionHeading } from './section-heading'

const GOALS = [
  {
    icon: Zap,
    label: 'Fast validation',
    description: 'Deterministic checks — tests, lint, type — run in parallel. Security review adds a diff-based pass on top.',
  },
  {
    icon: Server,
    label: 'Self-hosted',
    description: 'Runs on developer hardware. No cloud dependency, no SaaS lock-in. Your data stays on your machine.',
  },
  {
    icon: Cpu,
    label: 'Low cost',
    description: 'Use cloud models (gpt-4o, Claude) or switch to local models via Ollama for near-zero token cost.',
  },
  {
    icon: Layers,
    label: 'Lightweight',
    description: 'SQLite-first storage, no Kafka or Elasticsearch. Minimal profile runs only 4 core services.',
  },
  {
    icon: Lock,
    label: 'Security by default',
    description: 'Container isolation, secret redaction, SSRF protection, and approval gates are on by default.',
  },
  {
    icon: Terminal,
    label: 'Modular',
    description: 'Each service has a clear boundary. Add or remove services without breaking the rest of the system.',
  },
] as const

export function PerformanceMetrics() {
  return (
    <section id="metrics" aria-labelledby="metrics-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="metrics-title"
        label="Design goals"
        title={
          <>
            Built for
            <span className="text-signal"> your machine.</span>
          </>
        }
        lead="Evershade is designed to run locally, stay fast, and keep costs low. These are the principles that guide every architectural decision."
      />

      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 md:mt-24">
        {GOALS.map((goal) => {
          const Icon = goal.icon
          return (
            <div
              key={goal.label}
              className="group border border-border p-6 transition-colors hover:border-signal"
            >
              <div className="flex items-center gap-3">
                <span className="flex size-10 items-center justify-center border border-foreground/40 group-hover:border-signal">
                  <Icon className="size-5 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
                </span>
                <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{goal.label}</p>
              </div>
              <p className="mt-4 text-sm leading-snug text-muted-foreground">{goal.description}</p>
            </div>
          )
        })}
      </div>

      <div className="mt-24 grid gap-12 md:grid-cols-12 md:gap-8">
        <div className="md:col-span-7">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Mission lifecycle'}</p>
          <div className="mt-6 overflow-hidden border border-border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-card">
                  <th className="px-4 py-3 text-left font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                    Phase
                  </th>
                  <th className="px-4 py-3 text-left font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                    What happens
                  </th>
                </tr>
              </thead>
              <tbody>
                {[
                  { phase: 'Plan', detail: 'LLM breaks the task into milestones and features' },
                  { phase: 'Execute', detail: 'Workers run features in parallel, streaming logs live' },
                  { phase: 'Validate', detail: 'Tests, lint, type checks, and security review' },
                  { phase: 'Fix', detail: 'Failures become fix features and re-run automatically' },
                  { phase: 'Complete', detail: 'All checks pass, mission is recorded and archived' },
                ].map((row, i, arr) => (
                  <tr key={row.phase} className={i < arr.length - 1 ? 'border-b border-border' : ''}>
                    <td className="px-4 py-3 font-semibold tracking-tight">{row.phase}</td>
                    <td className="px-4 py-3 text-muted-foreground">{row.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="md:col-span-4 md:col-start-9">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Cost control'}</p>
          <dl className="mt-6 space-y-4 border-t border-foreground pt-6">
            <div>
              <dt className="flex items-center gap-2 font-semibold tracking-tight">
                <Box className="size-4 text-signal-ink" aria-hidden="true" />
                Local models
              </dt>
              <dd className="mt-1 text-sm leading-snug text-muted-foreground">
                {'Switch to Ollama with a local LLM and eliminate cloud token costs entirely. Trade-off: slower planning, lower quality.'}
              </dd>
            </div>
            <div>
              <dt className="flex items-center gap-2 font-semibold tracking-tight">
                <Layers className="size-4 text-signal-ink" aria-hidden="true" />
                Caching
              </dt>
              <dd className="mt-1 text-sm leading-snug text-muted-foreground">
                {'Gobber caches embeddings and graph results. Repeated queries hit the cache, not the LLM.'}
              </dd>
            </div>
            <div>
              <dt className="flex items-center gap-2 font-semibold tracking-tight">
                <Server className="size-4 text-signal-ink" aria-hidden="true" />
                Minimal profile
              </dt>
              <dd className="mt-1 text-sm leading-snug text-muted-foreground">
                {'Run only core services (4 instead of 8) to halve memory usage. Perfect for CI/CD pipelines.'}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </section>
  )
}
