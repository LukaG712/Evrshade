'use client'

import { useEffect, useState } from 'react'
import { ArrowUpRight, Menu, X } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'
import { useI18n } from '@/lib/i18n'
import { LanguageSelector } from './language-selector'
import { ThemeToggle } from './theme-toggle'

const NAV_KEYS = [
  { href: '#overview', key: 'nav.overview' },
  { href: '#how-it-works', key: 'nav.how-it-works' },
  { href: '#platform', key: 'nav.platform' },
  { href: '#get-started', key: 'nav.get-started' },
  { href: '/compare', key: 'nav.compare' },
  { href: '/blog', key: 'nav.blog' },
  { href: '#about', key: 'nav.about' },
  { href: '#roadmap', key: 'nav.roadmap' },
]

export function MobileNav() {
  const [open, setOpen] = useState(false)
  const { t } = useI18n()

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
        className="inline-flex h-8 w-8 items-center justify-center rounded-sm border border-foreground transition-colors hover:bg-foreground hover:text-background focus-visible:outline-2 focus-visible:outline-offset-2"
        aria-label={t('header.toggle-menu')}
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
          <ul className="space-y-2">
            {NAV_KEYS.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className="block rounded-lg px-3 py-3 text-base font-medium text-foreground transition-colors hover:bg-muted"
                >
                  {t(item.key)}
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
              className="inline-flex h-10 flex-1 items-center justify-center gap-1.5 rounded-sm border border-foreground px-3 text-sm font-medium transition-colors hover:bg-foreground hover:text-background focus-visible:outline-2 focus-visible:outline-offset-2"
            >
              {t('hero.github')}
              <ArrowUpRight className="size-3.5" aria-hidden="true" />
            </a>
            <LanguageSelector />
            <ThemeToggle />
          </div>
        </nav>
      </div>
    </div>
  )
}
