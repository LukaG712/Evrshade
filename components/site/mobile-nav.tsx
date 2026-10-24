'use client'

import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import { ThemeToggle } from './theme-toggle'

const NAV = [
  { href: '#overview', label: 'Overview' },
  { href: '#how-it-works', label: 'How It Works' },
  { href: '#platform', label: 'Platform' },
  { href: '#get-started', label: 'Get Started' },
  { href: '#about', label: 'About' },
  { href: '#roadmap', label: 'Roadmap' },
  { href: '/blog', label: 'Blog' },
  { href: '/compare', label: 'Compare' },
]

export function MobileNav() {
  const [open, setOpen] = useState(false)

  return (
    <div className="lg:hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex h-10 w-10 items-center justify-center border border-border transition-colors hover:bg-muted active:scale-95"
        aria-label="Toggle menu"
        aria-expanded={open}
      >
        {open ? <X className="size-5" /> : <Menu className="size-5" />}
      </button>
      {open && (
        <div className="absolute left-0 right-0 top-16 z-50 border-b border-border bg-background/95 backdrop-blur-lg">
          <nav aria-label="Mobile" className="px-4 py-4">
            <ul className="space-y-1">
              {NAV.map((item) => (
                <li key={item.href}>
                  <a
                    href={item.href}
                    onClick={() => setOpen(false)}
                    className="block rounded-lg px-3 py-3 text-base font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground active:bg-muted"
                  >
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
            <div className="mt-4 flex items-center gap-2 border-t border-border pt-4">
              <ThemeToggle />
            </div>
          </nav>
        </div>
      )}
    </div>
  )
}
