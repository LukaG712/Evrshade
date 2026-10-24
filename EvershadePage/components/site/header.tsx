import { ArrowUpRight } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'

const NAV = [
  { href: '#console', label: 'Console', index: '02' },
  { href: '#missions', label: 'Missions', index: '03' },
  { href: '#trace', label: 'Trace', index: '04' },
  { href: '#harness', label: 'Harness', index: '05' },
  { href: '#security', label: 'Trust', index: '06' },
  { href: '#architecture', label: 'Architecture', index: '07' },
  { href: '#integrations', label: 'Integrations', index: '08' },
  { href: '#cli', label: 'CLI', index: '09' },
  { href: '#install', label: 'Install', index: '10' },
  { href: '#changelog', label: 'Changelog', index: '11' },
  { href: '#roadmap', label: 'Roadmap', index: '12' },
  { href: '#api', label: 'API', index: '13' },
  { href: '#why', label: 'Why', index: '14' },
  { href: '#use-cases', label: 'Use cases', index: '15' },
  { href: '#slammer', label: 'Slammer', index: '16' },
]

export function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-border bg-background/85 backdrop-blur-md">
      <div className="flex h-14 items-center justify-between px-4 md:px-[max(24px,3vw)]">
        <a href="#top" className="flex items-center gap-2.5 focus-visible:outline-2 focus-visible:outline-offset-4">
          <span className="grid size-5 grid-cols-2 gap-px" aria-hidden="true">
            <span className="bg-foreground" />
            <span className="bg-foreground" />
            <span className="bg-foreground" />
            <span className="bg-signal" />
          </span>
          <span className="text-sm font-semibold tracking-tight">Evershade</span>
        </a>
        <nav aria-label="Primary" className="hidden lg:block">
          <ul className="flex items-center gap-6 font-mono xl:gap-8 text-[11px] uppercase tracking-wider">
            {NAV.map((item) => (
              <li key={item.href}>
                <a href={item.href} className="group flex items-center gap-1.5 text-muted-foreground transition-colors hover:text-foreground">
                  <span className="text-foreground/30 transition-colors group-hover:text-signal-ink">{item.index}</span>
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <a
          href={REPO_URL}
          target="_blank"
          rel="noreferrer"
          className="inline-flex h-8 items-center gap-1.5 border border-foreground px-3 font-mono text-[11px] uppercase tracking-wider transition-colors hover:bg-foreground hover:text-background"
        >
          GitHub
          <ArrowUpRight className="size-3.5" aria-hidden="true" />
        </a>
      </div>
    </header>
  )
}
