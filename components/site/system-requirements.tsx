import { Cpu, HardDrive, Monitor, Server } from 'lucide-react'
import { SectionHeading } from './section-heading'

const REQUIREMENTS = [
  {
    icon: Cpu,
    title: 'CPU',
    detail: '2 cores minimum, 4+ recommended for parallel workers',
  },
  {
    icon: HardDrive,
    title: 'RAM',
    detail: '4 GB minimum, 8 GB+ recommended with local LLMs',
  },
  {
    icon: Server,
    title: 'Storage',
    detail: '2 GB for services, additional space for models and data',
  },
  {
    icon: Monitor,
    title: 'Docker',
    detail: 'Docker 24+ and Docker Compose v2 required',
  },
]

export function SystemRequirements() {
  return (
    <section id="system-requirements" aria-labelledby="sysreq-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="sysreq-title"
        title={
          <>
            <span>System requirements.</span>
          </>
        }
        lead="Evershade runs on ordinary developer hardware. No cloud dependency, no special GPU required unless you use local LLMs."
      />

      <div className="mt-16 stagger grid gap-4 sm:grid-cols-2 lg:grid-cols-4 md:mt-24">
        {REQUIREMENTS.map((req) => {
          const Icon = req.icon
          return (
            <div
              key={req.title}
              className="border border-border p-5"
            >
              <Icon className="size-5 text-muted-foreground" aria-hidden="true" />
              <p className="mt-3 font-semibold tracking-tight">{req.title}</p>
              <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{req.detail}</p>
            </div>
          )
        })}
      </div>
    </section>
  )
}
