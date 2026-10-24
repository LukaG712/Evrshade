import { ArrowUpRight } from 'lucide-react'
import { VERSION, REPO_URL } from '@/lib/evershade'

const LATEST_CHANGES = [
  'Mission fix-revalidate loop with configurable retries',
  'SSE streaming for real-time mission logs',
  'AES-256-GCM encrypted secrets management',
  'Container and workstation isolation levels',
  'Plugin registry for MCP tool extensions',
]

export function ChangelogTicker() {
  return (
    <section id="changelog" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <div className="grid gap-10 md:grid-cols-12">
        <div className="md:col-span-7">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'11 — Latest release'}</p>
          <h2 className="mt-4 text-4xl font-semibold leading-[0.9] tracking-[-0.05em] text-balance md:text-6xl lg:text-7xl">
            Always moving
            <span className="text-signal">.</span>
          </h2>
          <p className="mt-6 max-w-2xl text-pretty text-lg leading-snug text-muted-foreground">
            Evershade ships fast. Every release adds capabilities, hardens security, and improves the developer experience.
          </p>

          <div className="mt-10 border border-foreground p-5">
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center rounded-full border border-signal bg-signal/10 px-2.5 py-0.5 font-mono text-[11px] font-bold uppercase tracking-wider text-signal-ink">
                {'v' + VERSION}
              </span>
              <time className="font-mono text-[11px] text-muted-foreground" dateTime="2025-10-24">
                Oct 2025
              </time>
            </div>
            <ul className="mt-4 space-y-2">
              {LATEST_CHANGES.map((change) => (
                <li key={change} className="flex items-start gap-2 text-sm leading-snug">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-signal-ink" />
                  {change}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="md:col-span-4 md:col-start-9">
          <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Release history'}</p>
          <div className="mt-6 space-y-0">
            {[
              { version: '1.13.0', date: 'Sep 2025', note: 'Mission Control lifecycle' },
              { version: '1.12.0', date: 'Aug 2025', note: 'Emergency stop & credential rotation' },
              { version: '1.11.0', date: 'Jul 2025', note: 'Single dashboard & MCP plugins' },
              { version: '1.10.0', date: 'Jun 2025', note: 'Agent eval suite & release signing' },
              { version: '1.9.0', date: 'May 2025', note: 'Agent workstations & live terminal' },
            ].map((release) => (
              <div key={release.version} className="border-b border-border py-4">
                <div className="flex items-baseline justify-between gap-4">
                  <span className="font-mono text-sm font-semibold">{release.version}</span>
                  <span className="font-mono text-[11px] text-muted-foreground">{release.date}</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{release.note}</p>
              </div>
            ))}
          </div>
          <a
            href={`${REPO_URL}/blob/main/CHANGELOG.md`}
            target="_blank"
            rel="noreferrer"
            className="group mt-6 inline-flex items-center gap-1 text-sm font-medium underline underline-offset-2 hover:text-signal-ink"
          >
            Full changelog
            <ArrowUpRight className="size-3.5 opacity-40 transition-opacity group-hover:opacity-100" aria-hidden="true" />
          </a>
        </div>
      </div>
    </section>
  )
}
