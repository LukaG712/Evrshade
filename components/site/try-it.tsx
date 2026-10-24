import { Play, Terminal } from 'lucide-react'
import { SectionHeading } from './section-heading'

export function TryIt() {
  return (
    <section id="try-it" aria-labelledby="try-it-title" className="px-4 pt-24 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="try-it-title"
        label="Try it"
        title={
          <>
            Start in
            <span className="text-signal"> under a minute.</span>
          </>
        }
        lead="No account needed. No cloud dependency. Just Docker and a terminal."
      />

      <div className="mt-16 grid gap-8 md:grid-cols-12 md:mt-24">
        <div className="md:col-span-8">
          {/* One-liner */}
          <div className="border border-border p-6">
            <div className="flex items-center gap-2">
              <Play className="size-4 text-signal-ink" aria-hidden="true" />
              <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'One-liner start'}</p>
            </div>
            <div className="mt-4 overflow-auto rounded border border-border bg-background p-4">
              <code className="font-mono text-sm">
                git clone https://github.com/LukaG712/Evershade.git &amp;&amp; cd Evershade &amp;&amp; cp .env.example .env &amp;&amp; docker compose --profile minimal up -d
              </code>
            </div>
            <p className="mt-3 text-sm text-muted-foreground">
              This clones the repo, copies the environment template, and starts the 4 core services in detached mode.
            </p>
          </div>

          {/* What you get */}
          <div className="mt-8 border border-border p-6">
            <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'What you get'}</p>
            <ul className="mt-4 space-y-3">
              {[
                'Greenie orchestrator on port 8080 — the main API entry point',
                'Slinker code execution on port 8000 — runs tests, lint, type checks',
                'Trapper web scraper on port 3000 — fetches and parses web content',
                'Gobber knowledge graph on port 8085 — stores and searches project memory',
              ].map((item) => (
                <li key={item} className="flex items-start gap-2 text-sm leading-snug text-muted-foreground">
                  <span className="mt-1.5 size-1 shrink-0 rounded-full bg-signal" aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="md:col-span-4">
          <div className="border border-border p-5">
            <div className="flex items-center gap-2">
              <Terminal className="size-4 text-signal-ink" aria-hidden="true" />
              <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Prerequisites'}</p>
            </div>
            <ul className="mt-4 space-y-3 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/40" aria-hidden="true" />
                Docker Desktop or Docker Engine installed
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/40" aria-hidden="true" />
                Git for cloning the repository
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/40" aria-hidden="true" />
                At least one LLM API key (or Ollama for local)
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/40" aria-hidden="true" />
                ~512MB RAM for minimal profile
              </li>
            </ul>
          </div>

          <div className="mt-6 rounded border border-dashed border-foreground/50 p-5">
            <p className="text-sm font-semibold tracking-tight">Want the full platform?</p>
            <p className="mt-2 text-sm text-muted-foreground">
              Replace <code className="font-mono text-xs">--profile minimal</code> with <code className="font-mono text-xs">--profile full</code> to start all 10 services including the Slammer dashboard.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
