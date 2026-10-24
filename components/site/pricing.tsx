import { Shield, Server, Terminal, Workflow, Eye, Lock, Network } from 'lucide-react'
import { SectionHeading } from './section-heading'

const FEATURES = [
  { icon: Workflow, title: '10 microservices', detail: 'All included, no add-ons' },
  { icon: Eye, title: 'Full observability', detail: 'Metrics, traces, and logs' },
  { icon: Lock, title: 'Knowledge graph', detail: 'Persistent memory across sessions' },
  { icon: Shield, title: 'Approval gates', detail: 'Human-in-the-loop control' },
  { icon: Server, title: 'Encrypted secrets', detail: 'AES-256-GCM at rest' },
  { icon: Network, title: 'Web dashboard', detail: 'React UI, real-time streaming' },
]

const COSTS = [
  { item: 'Docker Desktop', cost: 'Free' },
  { item: 'Your hardware', cost: 'Already owned' },
  { item: 'LLM API calls', cost: 'Pay-per-use' },
  { item: 'Domain (optional)', cost: '~$10/yr' },
  { item: 'Your time', cost: '~5 min to set up' },
]

export function Pricing() {
  return (
    <section id="pricing" aria-labelledby="pricing-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="pricing-title"
        label="Pricing"
        title={
          <>
            $0.
            <br />
            <span className="text-muted-foreground">Forever.</span>
          </>
        }
        lead="MIT License. Self-hosted. No telemetry. No credits. No rate limits. No vendor lock-in."
      />

      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((f) => {
          const Icon = f.icon
          return (
            <div key={f.title} className="border border-foreground p-5">
              <Icon className="size-5 text-muted-foreground" aria-hidden="true" />
              <p className="mt-3 text-lg font-semibold tracking-tight">{f.title}</p>
              <p className="mt-1 text-sm text-muted-foreground">{f.detail}</p>
            </div>
          )
        })}
      </div>

      <div className="mt-16 border border-foreground p-6">
        <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">What you actually pay</p>
        <dl className="mt-4 grid gap-3 sm:grid-cols-5">
          {COSTS.map((c) => (
            <div key={c.item}>
              <dt className="text-sm text-muted-foreground">{c.item}</dt>
              <dd className="mt-1 font-semibold">{c.cost}</dd>
            </div>
          ))}
        </dl>
      </div>

      <div className="mt-8 border border-dashed border-border p-6 text-center">
        <p className="text-sm text-muted-foreground">A cloud tier may come later. Self-hosted will always remain free.</p>
      </div>
    </section>
  )
}
