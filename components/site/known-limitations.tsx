import { AlertTriangle, Clock, Database, ShieldAlert } from 'lucide-react'
import { SectionHeading } from './section-heading'

const LIMITATIONS = [
  {
    icon: ShieldAlert,
    title: 'Beta maturity',
    description: 'All services are currently in beta. APIs may change between updates. Production use is at your own risk.',
  },
  {
    icon: Database,
    title: 'SQLite concurrency',
    description: 'SQLite handles read-heavy workloads well but may bottleneck under heavy concurrent writes. Consider PostgreSQL for multi-user setups.',
  },
  {
    icon: Clock,
    title: 'No real-time sync',
    description: 'Multi-instance setups do not share state in real time. Each Evershade instance runs independently.',
  },
  {
    icon: AlertTriangle,
    title: 'Model dependency',
    description: 'Mission quality depends on the LLM provider. Local models via Ollama are slower and less capable than cloud models.',
  },
]

export function KnownLimitations() {
  return (
    <section id="limitations" aria-labelledby="limitations-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="limitations-title"
        label="Known limitations"
        title={
          <>
            What it <span className="text-signal">doesn't</span> do yet.
          </>
        }
        lead="Evershade is under active development. These are the current boundaries of the platform."
      />

      <div className="mt-16 grid gap-4 sm:grid-cols-2 md:mt-24">
        {LIMITATIONS.map((item) => {
          const Icon = item.icon
          return (
            <div key={item.title} className="border border-border p-6">
              <div className="flex items-center gap-3">
                <Icon className="size-5 text-muted-foreground" aria-hidden="true" />
                <p className="font-semibold tracking-tight">{item.title}</p>
              </div>
              <p className="mt-3 text-sm leading-snug text-muted-foreground">{item.description}</p>
            </div>
          )
        })}
      </div>
    </section>
  )
}
