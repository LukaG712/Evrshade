'use client'

import { useState } from 'react'
import { Menu, X } from 'lucide-react'

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

  return (
    <div className="lg:hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex h-10 w-10 items-center justify-center rounded border border-foreground p-0 transition-colors hover:bg-foreground hover:text-background active:scale-95"
        aria-label="Toggle menu"
        aria-expanded={open}
      >
        {open ? <X className="size-5" /> : <Menu className="size-5" />}
      </button>
      {open && (
        <div className="absolute left-0 right-0 top-14 z-50 border-b border-border bg-background/95 backdrop-blur-md">
          <nav aria-label="Mobile" className="px-4 py-4">
            <ul className="space-y-1">
              {NAV.map((item) => (
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
            </ul>
          </nav>
        </div>
      )}
    </div>
  )
}
