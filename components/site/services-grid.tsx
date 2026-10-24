import {
  Brain, Bug, Code2, Database, Eye, Lock, Network, Terminal,
  Webhook, Workflow,
} from 'lucide-react'
import { SERVICES, TIER_LABEL, type Service } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const ICONS: Record<string, React.ElementType> = {
  greenie: Workflow,
  slinker: Code2,
  trapper: Bug,
  gobber: Database,
  shrewd: Brain,
  sneaker: Eye,
  hider: Lock,
  poltergeist: Webhook,
  slammer: Network,
  speedy: Terminal,
}

const TIER_DOT: Record<string, string> = {
  orchestrator: 'bg-signal',
  core: 'bg-foreground',
  optional: 'border border-foreground bg-transparent',
  client: 'border border-foreground bg-transparent',
}

export function ServicesGrid() {
  return (
    <section id="services-grid" aria-labelledby="services-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="services-title"
        label="Services"
        title={
          <>
            Ten services,
            <br />
            <span className="text-muted-foreground">one platform.</span>
          </>
        }
        lead="Each microservice has a single responsibility, talks over HTTP, and can run independently while contributing to the whole."
      />

      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {SERVICES.map((svc: Service, i: number) => {
          const Icon = ICONS[svc.id]
          return (
            <div
              key={svc.id}
              className="group border border-foreground p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="flex items-center gap-2">
                <span className={`size-1.5 rounded-full ${TIER_DOT[svc.tier]}`} aria-hidden="true" />
                <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  {String(i + 1).padStart(2, '0')}
                </span>
              </div>
              {Icon && (
                <Icon className="mt-4 size-5 text-muted-foreground transition-colors group-hover:text-signal-ink" aria-hidden="true" />
              )}
              <p className="mt-3 text-lg font-semibold tracking-tight">{svc.name}</p>
              <p className="mt-1 text-sm leading-snug text-muted-foreground">{svc.role}</p>
              <div className="mt-3 flex items-center justify-between">
                <span className="font-mono text-[10px] text-muted-foreground">
                  {svc.port === 'CLI' ? 'CLI' : `:${svc.port}`}
                </span>
                <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  {TIER_LABEL[svc.tier]}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
