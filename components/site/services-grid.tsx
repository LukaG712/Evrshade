'use client'

import { useEffect, useRef } from 'react'
import { Brain, Bug, Code2, Database, Eye, Lock, Network, Terminal, Webhook, Workflow } from 'lucide-react'
import { SERVICES, TIER_LABEL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const SERVICE_ICON: Record<string, typeof Brain> = {
  greenie: Workflow,    // orchestrator & API backend
  slinker: Code2,        // code execution engine
  trapper: Bug,          // web scraping & crawling
  gobber: Database,      // persistent storage & knowledge graph
  shrewd: Brain,          // LLM provider abstraction
  sneaker: Eye,           // metrics, traces, logs
  hider: Lock,            // encrypted secrets management
  poltergeist: Webhook,   // notifications & async delivery
  slammer: Network,       // React web dashboard
  speedy: Terminal,       // CLI
}

export function ServicesGrid() {
  const gridRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = gridRef.current
    if (!el) return
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.classList.add('visible')
          observer.disconnect()
        }
      },
      { threshold: 0.05 }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return (
    <section id="services" aria-labelledby="services-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="services-title"
        label="Services"
        title={
          <>Ten services, one platform<span className="text-signal">.</span></>
        }
        lead="Each service has a single responsibility, a public API, and runs in its own container. Mix and match via compose profiles."
      />

      <div ref={gridRef} className="mt-16 stagger grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 md:mt-24">
        {SERVICES.map((service) => {
          const Icon = SERVICE_ICON[service.id] || Workflow
          return (
            <div
              key={service.id}
              className="group border border-border p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-signal hover:shadow-md"
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
