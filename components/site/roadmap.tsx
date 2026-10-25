import { ArrowUpRight, CheckCircle, Clock, Circle } from 'lucide-react'
import { OPEN_ITEMS, REPO_URL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const SHIPPED = [
  'Greenie orchestrator and API backend',
  'Slinker code execution engine',
  'Trapper web scraping and crawling',
  'Gobber knowledge graph and storage',
  'Shrewd LLM provider abstraction',
  'Hider encrypted secrets management',
  'Poltergeist notification delivery',
  'Slammer React dashboard',
  'Speedy CLI',
  'Mission lifecycle with fix-revalidate',
  'SSE streaming for mission logs',
  'Plugin registry for MCP tools',
]

const IN_PROGRESS = [
  'Sneaker: SQLite persistence for metrics, traces and logs',
]

const PLANNED = [
  'Spec mode with droids and skills',
  'Container and workstation isolation',
  'Alert rules and deduplication',
  'Workflow triggers and visual builder',
  'Agent eval suite',
  'Emergency stop and activity timeline',
]

export function Roadmap() {
  return (
    <section id="roadmap" aria-labelledby="roadmap-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="roadmap-title"
        label="Roadmap"
        title={
          <>
            What's
            <span className="text-signal"> shipped.</span>
            <br />
            <span className="text-muted-foreground">What's next.</span>
          </>
        }
        lead="Evershade is open source and actively developed. See what's already available, what's in progress, and what's planned."
      />

      <div className="mt-16 grid gap-6 md:mt-24 md:grid-cols-3">
        <div className="border border-border p-5">
          <div className="flex items-center gap-2">
            <CheckCircle className="size-4 text-signal" aria-hidden="true" />
            <p className="font-semibold tracking-tight">Shipped</p>
          </div>
          <ul className="mt-3 space-y-2">
            {SHIPPED.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm leading-snug text-muted-foreground">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-signal" aria-hidden="true" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div className="border border-border p-5">
          <div className="flex items-center gap-2">
            <Clock className="size-4 text-foreground" aria-hidden="true" />
            <p className="font-semibold tracking-tight">In progress</p>
          </div>
          <ul className="mt-3 space-y-2">
            {IN_PROGRESS.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm leading-snug text-muted-foreground">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/40" aria-hidden="true" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div className="border border-border p-5">
          <div className="flex items-center gap-2">
            <Circle className="size-4 text-muted-foreground" aria-hidden="true" />
            <p className="font-semibold tracking-tight">Planned</p>
          </div>
          <ul className="mt-3 space-y-2">
            {PLANNED.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm leading-snug text-muted-foreground">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/20" aria-hidden="true" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-8 flex flex-col gap-4 border border-dashed border-foreground/50 p-5 md:flex-row md:items-center md:justify-between">
        <div className="flex items-start gap-3">
          <span className="mt-1 size-3 shrink-0 border border-foreground" aria-hidden="true" />
          <div>
            <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Open items'}</p>
            {OPEN_ITEMS.map((o) => (
              <p key={o} className="mt-1 font-medium">
                {o}
              </p>
            ))}
          </div>
        </div>
        <a
          href={`${REPO_URL}/blob/master/ROADMAP.md`}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-wider hover:text-signal-ink"
        >
          Read ROADMAP.md
          <ArrowUpRight className="size-3.5" aria-hidden="true" />
        </a>
      </div>
    </section>
  )
}
