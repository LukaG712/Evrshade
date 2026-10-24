'use client'

import { useEffect, useState } from 'react'
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

export function MobileNav() {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [open])

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
      <div
        className={`absolute left-0 right-0 top-14 z-50 border-b border-border bg-background/95 backdrop-blur-md transition-all duration-200 ease-in-out ${
          open ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
        }`}
        style={{ transform: open ? 'translateY(0)' : 'translateY(-8px)' }}
      >
        <nav aria-label="Mobile" className="px-4 py-4">
          <ul className="space-y-1 font-mono text-[11px] uppercase tracking-wider">
            {NAV.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className="flex items-center gap-2 py-3 text-muted-foreground transition-colors hover:text-foreground"
                >
                  <span className="text-foreground/30">{item.index}</span>
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
          <div className="mt-4 flex items-center gap-3 border-t border-border pt-4">
            <a
              href={REPO_URL}
              target="_blank"
              rel="noreferrer"
              onClick={() => setOpen(false)}
              className="inline-flex h-10 flex-1 items-center justify-center gap-1.5 border border-foreground px-3 font-mono text-[11px] uppercase tracking-wider transition-colors hover:bg-foreground hover:text-background"
            >
              GitHub
              <ArrowUpRight className="size-3.5" aria-hidden="true" />
            </a>
            <ThemeToggle />
          </div>
        </nav>
      </div>
    </div>
  )
}
