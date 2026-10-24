import { Box, Cpu, Database, Eye, Lock, Server, Terminal, Wifi, Zap } from 'lucide-react'
import { SERVICES, TIER_LABEL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const TIER_ICON: Record<string, typeof Box> = {
  orchestrator: Zap,
  core: Server,
  optional: Box,
  client: Terminal,
}

export function ServicesGrid() {
  return (
    <section id="services" aria-labelledby="services-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="services-title"
        label="Services"
        title={
          <>
            Ten services,
            <span className="text-signal"> one platform.</span>
          </>
        }
        lead="Each service has a single responsibility, a public API, and runs in its own container. Mix and match via compose profiles."
      />

      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 md:mt-24">
        {SERVICES.map((service) => {
          const Icon = TIER_ICON[service.tier] || Box
          return (
            <div
              key={service.id}
              className="group border border-border p-5 transition-colors hover:border-signal"
            >
              <div className="flex items-center gap-2">
                <span className="flex size-8 items-center justify-center border border-foreground/40 group-hover:border-signal">
                  <Icon className="size-4 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
                </span>
                <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  {TIER_LABEL[service.tier]}
                </p>
              </div>
              <p className="mt-4 text-lg font-semibold tracking-tight">{service.name}</p>
              <p className="mt-1 text-sm text-muted-foreground">{service.role}</p>
              <div className="mt-3 flex items-center gap-2">
                <span className="font-mono text-xs text-muted-foreground">Port {service.port}</span>
                <span className="text-muted-foreground/40">·</span>
                <span className="font-mono text-xs text-muted-foreground">{service.stack}</span>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
