'use client'

import { useState } from 'react'
import { Menu, X } from 'lucide-react'

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
  { href: '#knowledge-graph', label: 'Graph', index: '17' },
  { href: '#metrics', label: 'Metrics', index: '18' },
  { href: '#community', label: 'Community', index: '19' },
]

export function MobileNav() {
  const [open, setOpen] = useState(false)

  return (
    <div className="lg:hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex h-8 items-center justify-center rounded border border-foreground p-1.5 transition-colors hover:bg-foreground hover:text-background"
        aria-label="Toggle menu"
        aria-expanded={open}
      >
        {open ? <X className="size-4" /> : <Menu className="size-4" />}
      </button>
      {open && (
        <div className="absolute left-0 right-0 top-14 z-50 border-b border-border bg-background/95 backdrop-blur-md">
          <nav aria-label="Mobile" className="px-4 py-4">
            <ul className="space-y-1 font-mono text-[11px] uppercase tracking-wider">
              {NAV.map((item) => (
                <li key={item.href}>
                  <a
                    href={item.href}
                    onClick={() => setOpen(false)}
                    className="flex items-center gap-2 py-2 text-muted-foreground transition-colors hover:text-foreground"
                  >
                    <span className="text-foreground/30">{item.index}</span>
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      )}
    </div>
  )
}
