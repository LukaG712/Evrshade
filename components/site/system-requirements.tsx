import { Cpu, HardDrive, Monitor, Server } from 'lucide-react'
import { SectionHeading } from './section-heading'

const SPECS = [
  { icon: Cpu, label: 'CPU', value: '2 cores', detail: 'x86_64 or ARM64' },
  { icon: Monitor, label: 'RAM', value: '4 GB', detail: '8 GB recommended' },
  { icon: HardDrive, label: 'Storage', value: '2 GB', detail: 'SSD recommended' },
  { icon: Server, label: 'Docker', value: '20.10+', detail: 'With Compose v2' },
]

export function SystemRequirements() {
  return (
    <section id="system-requirements" aria-labelledby="sysreq-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="sysreq-title"
        label="System requirements"
        title={
          <>
            What you need,
            <br />
            <span className="text-muted-foreground">probably already have it.</span>
          </>
        }
        lead="Evershade runs on ordinary developer hardware. No GPU required — the LLM calls happen over the network."
      />

      <div className="mt-16 grid gap-4 sm:grid-cols-2 md:grid-cols-4">
        {SPECS.map((spec) => {
          const Icon = spec.icon
          return (
            <div key={spec.label} className="border border-foreground p-5">
              <Icon className="size-5 text-muted-foreground" aria-hidden="true" />
              <p className="mt-4 text-2xl font-semibold tracking-tight">{spec.value}</p>
              <p className="mt-1 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{spec.label}</p>
              <p className="mt-2 text-sm text-muted-foreground">{spec.detail}</p>
            </div>
          )
        })}
      </div>
    </section>
  )
}
