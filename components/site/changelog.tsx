import { ArrowUpRight } from 'lucide-react'
import { REPO_URL, ROADMAP, VERSION } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

export function Changelog() {
  return (
    <section id="changelog" aria-labelledby="changelog-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="changelog-title"
        label="Changelog"
        title={
          <>
            Development
            <br />
            <span className="text-muted-foreground">timeline.</span>
          </>
        }
        lead={`Currently at v${VERSION}. Evershade is under active development — track progress through the phases below.`}
      />

      <div className="mt-16 space-y-4">
        {ROADMAP.map((phase) => (
          <div key={phase.phase} className="border border-foreground p-5">
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center rounded-full border border-signal bg-signal/10 px-2.5 py-0.5 font-mono text-[11px] font-bold uppercase tracking-wider text-signal-ink">
                Phase {phase.phase}
              </span>
              <p className="font-semibold tracking-tight">{phase.name}</p>
            </div>
            <ul className="mt-3 space-y-1">
              {phase.items.map((item) => (
                <li key={item} className="flex items-start gap-2 text-sm leading-snug text-muted-foreground">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-signal-ink" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="mt-8 border border-dashed border-foreground/50 p-5">
        <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Source code'}</p>
        <p className="mt-2 text-sm text-muted-foreground">
          Browse the full source code, open issues, and contribute on GitHub.
        </p>
        <a
          href={REPO_URL}
          target="_blank"
          rel="noreferrer"
          className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium underline underline-offset-2 hover:text-signal-ink"
        >
          View on GitHub
          <ArrowUpRight className="size-3.5" aria-hidden="true" />
        </a>
      </div>
    </section>
  )
}
