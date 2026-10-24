import { ArrowUpRight } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'
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
    <section id="roadmap" aria-labelledby="roadmap-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <SectionHeading
          id="roadmap-title"
          label="What's next"
          title={
            <>Under construction<span className="text-signal">.</span></>
          }
          lead="Evershade is actively developed. These are the current focus areas - not a list of finished features."
        />
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

      <div className="mt-12 stagger grid gap-4 sm:grid-cols-2 md:mt-24 lg:grid-cols-4">
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
    </section>
  )
}
