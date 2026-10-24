import { Box, Check, ChevronRight, Settings, Terminal } from 'lucide-react'
import { PROFILES } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

export function DockerCompose() {
  return (
    <section id="docker-compose" aria-labelledby="docker-compose-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
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

      <div className="mt-12 grid gap-6 md:grid-cols-12 md:mt-24">
        {/* Compose profiles */}
        <div className="md:col-span-7">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Compose profiles'}</p>
          <div className="mt-6 space-y-3">
            {PROFILES.map((profile) => (
              <div
                key={profile.name}
                className="flex items-center gap-3 border border-border p-3 transition-colors hover:border-signal sm:gap-4 sm:p-4"
              >
                <span className="flex size-7 shrink-0 items-center justify-center border border-foreground/40 sm:size-8">
                  <Box className="size-3.5 text-muted-foreground sm:size-4" aria-hidden="true" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold tracking-tight sm:text-base">{profile.name}</p>
                  <p className="truncate text-xs text-muted-foreground sm:text-sm">{profile.detail}</p>
                </div>
                <code className="shrink-0 font-mono text-[10px] text-muted-foreground sm:text-xs">{profile.flag}</code>
              </div>
            ))}
          </div>
        </div>

        {/* Quick start */}
        <div className="md:col-span-5">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Quick start'}</p>
          <div className="mt-6 space-y-4">
            <div className="border border-border p-3 sm:p-4">
              <div className="flex items-center gap-2">
                <span className="flex size-5 items-center justify-center rounded-full bg-signal sm:size-6">
                  <span className="text-xs font-semibold text-background">1</span>
                </span>
                <p className="text-sm font-semibold tracking-tight">Clone the repo</p>
              </div>
              <div className="mt-2 overflow-x-auto rounded border border-border bg-background p-2 sm:p-3">
                <code className="font-mono text-[10px] sm:text-xs">git clone https://github.com/LukaG712/Evershade.git</code>
              </div>
            </div>

            <div className="border border-border p-3 sm:p-4">
              <div className="flex items-center gap-2">
                <span className="flex size-5 items-center justify-center rounded-full bg-signal sm:size-6">
                  <span className="text-xs font-semibold text-background">2</span>
                </span>
                <p className="text-sm font-semibold tracking-tight">Copy environment file</p>
              </div>
              <div className="mt-2 overflow-x-auto rounded border border-border bg-background p-2 sm:p-3">
                <code className="font-mono text-[10px] sm:text-xs">cp .env.example .env</code>
              </div>
            </div>

            <div className="border border-border p-3 sm:p-4">
              <div className="flex items-center gap-2">
                <span className="flex size-5 items-center justify-center rounded-full bg-signal sm:size-6">
                  <span className="text-xs font-semibold text-background">3</span>
                </span>
                <p className="text-sm font-semibold tracking-tight">Start the services</p>
              </div>
              <div className="mt-2 overflow-x-auto rounded border border-border bg-background p-2 sm:p-3">
                <code className="font-mono text-[10px] sm:text-xs">docker compose --profile standard up -d</code>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Docker Compose structure */}
      <div className="mt-12 border border-border p-4 sm:p-6 md:mt-24">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'docker-compose.yml structure'}</p>
        <div className="mt-4 overflow-x-auto rounded border border-border bg-background p-3 sm:p-4">
          <pre className="font-mono text-[10px] leading-relaxed text-muted-foreground sm:text-xs">
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
