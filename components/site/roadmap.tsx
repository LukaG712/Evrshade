import { ArrowUpRight, Check } from 'lucide-react'
import { OPEN_ITEMS, REPO_URL, ROADMAP } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

export function Roadmap() {
  return (
    <section id="roadmap" aria-labelledby="roadmap-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="roadmap-title"
        index="12"
        label="Status"
        title={
          <>
            Nine phases shipped.
            <br />
            <span className="text-muted-foreground">Built in the open.</span>
          </>
        }
        lead="Every claim on this page maps to a checked item in the public roadmap. What isn't done is listed too."
      />

      <ol className="mt-16 grid border-t border-l border-foreground sm:grid-cols-3 md:mt-24 lg:grid-cols-9">
        {ROADMAP.map((p) => (
          <li key={p.phase} className="flex flex-col border-r border-b border-foreground p-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[11px] text-muted-foreground">{`P${p.phase}`}</span>
              <span className="grid size-4 place-items-center bg-signal" aria-label="shipped">
                <Check className="size-3" aria-hidden="true" />
              </span>
            </div>
            <p className="mt-8 text-lg font-semibold leading-tight tracking-tight">{p.name}</p>
            <ul className="mt-3 space-y-1">
              {p.items.map((it) => (
                <li key={it} className="text-xs leading-snug text-muted-foreground">
                  {it}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ol>

      <div className="mt-8 flex flex-col gap-4 border border-dashed border-foreground/50 p-5 md:flex-row md:items-center md:justify-between">
        <div className="flex items-start gap-3">
          <span className="mt-1 size-3 shrink-0 border border-foreground" aria-hidden="true" />
          <div>
            <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Open'}</p>
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
