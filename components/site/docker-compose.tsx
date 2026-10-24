import { Box, Check, ChevronRight, Settings, Terminal } from 'lucide-react'
import { PROFILES } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

export function DockerCompose() {
  return (
    <section id="docker-compose" aria-labelledby="docker-compose-title" className="px-4 pt-24 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="docker-compose-title"
        label="Setup"
        title={
          <>
            Up and running
            <span className="text-signal"> in one command.</span>
          </>
        }
        lead="Evershade uses Docker Compose profiles to let you start with just the core services or spin up the full platform."
      />

      <div className="mt-16 grid gap-12 md:grid-cols-12 md:mt-24">
        {/* Compose profiles */}
        <div className="md:col-span-7">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Compose profiles'}</p>
          <div className="mt-6 space-y-3">
            {PROFILES.map((profile) => (
              <div
                key={profile.name}
                className="flex items-center gap-4 border border-border p-4 transition-colors hover:border-signal"
              >
                <span className="flex size-8 shrink-0 items-center justify-center border border-foreground/40">
                  <Box className="size-4 text-muted-foreground" aria-hidden="true" />
                </span>
                <div className="flex-1">
                  <p className="font-semibold tracking-tight">{profile.name}</p>
                  <p className="text-sm text-muted-foreground">{profile.detail}</p>
                </div>
                <code className="font-mono text-xs text-muted-foreground">{profile.flag}</code>
              </div>
            ))}
          </div>
        </div>

        {/* Quick start */}
        <div className="md:col-span-5">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Quick start'}</p>
          <div className="mt-6 space-y-4">
            <div className="border border-border p-4">
              <div className="flex items-center gap-2">
                <span className="flex size-6 items-center justify-center rounded-full bg-signal">
                  <span className="text-xs font-semibold text-background">1</span>
                </span>
                <p className="text-sm font-semibold tracking-tight">Clone the repo</p>
              </div>
              <div className="mt-3 overflow-auto rounded border border-border bg-background p-3">
                <code className="font-mono text-xs">git clone https://github.com/LukaG712/Evershade.git</code>
              </div>
            </div>

            <div className="border border-border p-4">
              <div className="flex items-center gap-2">
                <span className="flex size-6 items-center justify-center rounded-full bg-signal">
                  <span className="text-xs font-semibold text-background">2</span>
                </span>
                <p className="text-sm font-semibold tracking-tight">Copy environment file</p>
              </div>
              <div className="mt-3 overflow-auto rounded border border-border bg-background p-3">
                <code className="font-mono text-xs">cp .env.example .env</code>
              </div>
            </div>

            <div className="border border-border p-4">
              <div className="flex items-center gap-2">
                <span className="flex size-6 items-center justify-center rounded-full bg-signal">
                  <span className="text-xs font-semibold text-background">3</span>
                </span>
                <p className="text-sm font-semibold tracking-tight">Start the services</p>
              </div>
              <div className="mt-3 overflow-auto rounded border border-border bg-background p-3">
                <code className="font-mono text-xs">docker compose --profile standard up -d</code>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Docker Compose structure */}
      <div className="mt-16 border border-border p-6 md:mt-24">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'docker-compose.yml structure'}</p>
        <div className="mt-4 overflow-auto rounded border border-border bg-background p-4">
          <pre className="font-mono text-xs leading-relaxed text-muted-foreground">
{`services:
  greenie:
    build: ./services/greenie
    ports: ["8080:8080"]
    profiles: ["minimal", "standard", "full"]
    
  slinker:
    build: ./services/slinker
    ports: ["8000:8000"]
    profiles: ["minimal", "standard", "full"]
    
  trapper:
    build: ./services/trapper
    ports: ["3000:3000"]
    profiles: ["minimal", "standard", "full"]
    
  gobber:
    build: ./services/gobber
    ports: ["8085:8085"]
    profiles: ["minimal", "standard", "full"]
    
  # Optional services...
  slammer:
    build: ./services/slammer
    ports: ["5173:5173"]
    profiles: ["full"]`}
          </pre>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          Each service builds from its own directory. Use profiles to control which services start.
        </p>
      </div>
    </section>
  )
}
