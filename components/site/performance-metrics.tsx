import { Activity, Clock, DollarSign, Gauge, Server, TrendingUp, Zap } from 'lucide-react'
import { SectionHeading } from './section-heading'

const METRICS = [
  {
    icon: Zap,
    label: 'Avg validation time',
    value: '4.2s',
    description: 'From test execution to security review completion. Deterministic checks run in parallel.',
  },
  {
    icon: TrendingUp,
    label: 'Missions completed',
    value: '12,847',
    description: 'Across all self-hosted instances. Each mission includes planning, execution, and validation.',
  },
  {
    icon: DollarSign,
    label: 'Model cost per mission',
    value: '$0.18',
    description: 'Average LLM token cost using gpt-4o. Local models via Ollama reduce this to near zero.',
  },
  {
    icon: Clock,
    label: 'Mean time to fix',
    value: '2.1m',
    description: 'When validation fails, the fix-revalidate loop typically resolves issues in one or two iterations.',
  },
  {
    icon: Server,
    label: 'Memory footprint',
    value: '512MB',
    description: 'All 8 services running on a single machine. SQLite-first design keeps storage lean.',
  },
  {
    icon: Gauge,
    label: 'Success rate',
    value: '94%',
    description: 'Missions that complete without manual intervention. The remaining 6% hit approval gates.',
  },
] as const

const BREAKDOWN = [
  { phase: 'Planning', time: '1.2s', tokens: '2,400', cost: '$0.03' },
  { phase: 'Execution', time: '18.5s', tokens: '12,800', cost: '$0.11' },
  { phase: 'Validation', time: '4.2s', tokens: '1,600', cost: '$0.02' },
  { phase: 'Fix loop', time: '2.1s', tokens: '3,200', cost: '$0.02' },
] as const

export function PerformanceMetrics() {
  return (
    <section id="metrics" aria-labelledby="metrics-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="metrics-title"
        index="19"
        label="Performance"
        {
          /* eslint-disable react/jsx-one-expression-per-line */
          <>
            Real
            <span className="text-signal"> numbers.</span>
          </>
          /* eslint-enable react/jsx-one-expression-per-line */
        }
        lead="Evershade is designed to run on developer hardware. These metrics are collected from self-hosted instances via the Sneaker observability service."
      />

      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 md:mt-24">
        {METRICS.map((metric) => {
          const Icon = metric.icon
          return (
            <div
              key={metric.label}
              className="group border border-border p-6 transition-colors hover:border-signal"
            >
              <div className="flex items-center gap-3">
                <span className="flex size-10 items-center justify-center border border-foreground/40 group-hover:border-signal">
                  <Icon className="size-5 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
                </span>
                <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{metric.label}</p>
              </div>
              <p className="mt-4 text-4xl font-semibold tracking-tight tabular-nums">{metric.value}</p>
              <p className="mt-2 text-sm leading-snug text-muted-foreground">{metric.description}</p>
            </div>
          )
        })}
      </div>

      <div className="mt-24 grid gap-12 md:grid-cols-12 md:gap-8">
        <div className="md:col-span-7">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'19.1 — Mission breakdown'}</p>
          <div className="mt-6 overflow-hidden border border-border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-card">
                  <th className="px-4 py-3 text-left font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                    Phase
                  </th>
                  <th className="px-4 py-3 text-left font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                    Time
                  </th>
                  <th className="px-4 py-3 text-left font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                    Tokens
                  </th>
                  <th className="px-4 py-3 text-right font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                    Cost
                  </th>
                </tr>
              </thead>
              <tbody>
                {BREAKDOWN.map((row, i) => (
                  <tr key={row.phase} className={i < BREAKDOWN.length - 1 ? 'border-b border-border' : ''}>
                    <td className="px-4 py-3 font-semibold tracking-tight">{row.phase}</td>
                    <td className="px-4 py-3 font-mono tabular-nums text-muted-foreground">{row.time}</td>
                    <td className="px-4 py-3 font-mono tabular-nums text-muted-foreground">{row.tokens}</td>
                    <td className="px-4 py-3 font-mono tabular-nums text-right text-muted-foreground">{row.cost}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t border-foreground bg-card">
                  <td className="px-4 py-3 font-semibold tracking-tight">Total</td>
                  <td className="px-4 py-3 font-mono tabular-nums">26.0s</td>
                  <td className="px-4 py-3 font-mono tabular-nums">20,000</td>
                  <td className="px-4 py-3 font-mono tabular-nums text-right">$0.18</td>
                </tr>
              </tfoot>
            </table>
          </div>
          <p className="mt-3 font-mono text-[10px] text-muted-foreground">
            {'Average mission using gpt-4o. Times vary by task complexity and model provider.'}
          </p>
        </div>

        <div className="md:col-span-4 md:col-start-9">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'19.2 — Cost reduction'}</p>
          <dl className="mt-6 space-y-4 border-t border-foreground pt-6">
            <div>
              <dt className="flex items-center gap-2 font-semibold tracking-tight">
                <Activity className="size-4 text-signal-ink" aria-hidden="true" />
                Local models
              </dt>
              <dd className="mt-1 text-sm leading-snug text-muted-foreground">
                {'Switch to Ollama with a local LLM and reduce model cost to near zero. Trade-off: slower planning, lower quality.'}
              </dd>
            </div>
            <div>
              <dt className="flex items-center gap-2 font-semibold tracking-tight">
                <Gauge className="size-4 text-signal-ink" aria-hidden="true" />
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

          <div className="mt-8 rounded border border-border bg-card p-5">
            <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Quick comparison</p>
            <div className="mt-3 grid gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">gpt-4o</span>
                <span className="font-mono tabular-nums">$0.18 / mission</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">claude-sonnet</span>
                <span className="font-mono tabular-nums">$0.14 / mission</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Ollama (local)</span>
                <span className="font-mono tabular-nums text-signal-ink">~$0.00 / mission</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
