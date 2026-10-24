'use client'

import { useState } from 'react'
import { ArrowUpRight, Menu, X } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'
import { ThemeToggle } from './theme-toggle'

const NAV = [
  { href: '#overview', label: 'Overview', index: '01' },
  { href: '#how-it-works', label: 'How It Works', index: '02' },
  { href: '#platform', label: 'Platform', index: '03' },
  { href: '#get-started', label: 'Get Started', index: '04' },
  { href: '#about', label: 'About', index: '05' },
  { href: '#roadmap', label: 'Roadmap', index: '06' },
]

const SUB_NAV = [
  { href: '/subpage/docs/install', label: 'Install' },
  { href: '/subpage/docs/configuration', label: 'Configuration' },
  { href: '/subpage/docs/architecture', label: 'Architecture' },
  { href: '/subpage/docs/security', label: 'Security' },
  { href: '/subpage/services', label: 'Services' },
  { href: '/subpage/compare', label: 'Compare' },
  { href: '/subpage/pricing', label: 'Pricing' },
  { href: '/subpage/community', label: 'Community' },
  { href: '/subpage/changelog', label: 'Changelog' },
]

export function Header() {
  const [open, setOpen] = useState(false)

  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-border bg-background/85 backdrop-blur-md" style={{ paddingTop: 'env(safe-area-inset-top, 0)' }}>
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

        {/* Inline nav — visible on larger screens */}
        <nav aria-label="Primary" className="hidden lg:block">
          <ul className="flex items-center gap-6 font-mono text-[11px] uppercase tracking-wider">
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

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-8 items-center gap-1.5 border border-foreground px-3 font-mono text-[11px] uppercase tracking-wider transition-colors hover:bg-foreground hover:text-background"
          >
            GitHub
            <ArrowUpRight className="size-3.5" aria-hidden="true" />
          </a>
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="inline-flex size-8 items-center justify-center border border-foreground p-0 transition-colors hover:bg-foreground hover:text-background active:scale-95"
            aria-label="Toggle menu"
            aria-expanded={open}
          >
            {open ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
        </div>
      </div>
      {open && (
        <div className="absolute left-0 right-0 top-14 z-50 border-b border-border bg-background/95 backdrop-blur-md">
          <nav aria-label="Primary" className="px-4 py-4">
            <ul className="space-y-1">
              {SUB_NAV.map((item) => (
                <li key={item.href}>
                  <a
                    href={item.href}
                    onClick={() => setOpen(false)}
                    className="flex items-center gap-2 rounded-lg px-3 py-3 text-base text-muted-foreground transition-colors hover:bg-muted hover:text-foreground active:scale-[0.98]"
                  >
                    {item.label}
                  </a>
                </li>
              ))}
              <li>
                <a
                  href={REPO_URL}
                  target="_blank"
                  rel="noreferrer"
                  onClick={() => setOpen(false)}
                  className="flex items-center justify-center gap-1.5 rounded-lg border border-foreground px-3 py-3 font-mono text-[11px] uppercase tracking-wider transition-colors hover:bg-foreground hover:text-background"
                >
                  GitHub
                  <ArrowUpRight className="size-3.5" aria-hidden="true" />
                </a>
              </li>
            </ul>
          </nav>
        </div>
      )}
    </header>
  )
}
