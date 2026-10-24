import { ArrowUpRight } from 'lucide-react'
import { OPEN_ITEMS, REPO_URL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const FOCUS_AREAS = [
  {
    title: 'Core services',
    items: [
      'Greenie orchestrator and API backend',
      'Slinker code execution engine',
      'Trapper web scraping and crawling',
      'Gobber knowledge graph and storage',
    ],
  },
  {
    title: 'Agent harness',
    items: [
      'Spec mode with droids and skills',
      'Container and workstation isolation',
      'Hooks and environment configuration',
    ],
  },
  {
    title: 'Observability',
    items: [
      'Sneaker metrics, traces, and logs',
      'SQLite persistence for observability data',
      'Alert rules and deduplication',
    ],
  },
  {
    title: 'Developer experience',
    items: [
      'Speedy CLI with Rich terminal UI',
      'Slammer React dashboard',
      'Compose profiles for quick setup',
    ],
  },
] as const

export function Roadmap() {
  return (
    <section id="roadmap" aria-labelledby="roadmap-title" className="px-4 pt-24 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="roadmap-title"
        label="What's next"
        title={
          <>
            Under
            <span className="text-signal"> construction.</span>
          </>
        }
        lead="Evershade is actively developed. These are the current focus areas and open items — not a list of finished features."
      />

      <div className="mt-16 grid gap-6 sm:grid-cols-2 md:mt-24 lg:grid-cols-4">
        {FOCUS_AREAS.map((area) => (
          <div key={area.title} className="border border-border p-5">
            <p className="font-semibold tracking-tight">{area.title}</p>
            <ul className="mt-3 space-y-2">
              {area.items.map((item) => (
                <li key={item} className="flex items-start gap-2 text-sm leading-snug text-muted-foreground">
                  <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/40" aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
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
          href={`${REPO_URL}/blob/main/ROADMAP.md`}
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
