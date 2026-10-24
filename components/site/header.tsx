'use client'

import { ArrowUpRight } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'
import { useI18n } from '@/lib/i18n'
import { CommandPalette } from './command-palette'
import { LanguageSelector } from './language-selector'
import { MobileNav } from './mobile-nav'
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

export function Header() {
  const { t } = useI18n()
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-border bg-background/85 backdrop-blur-md">
      <div className="flex h-14 items-center justify-between px-4 lg:h-16 lg:px-[max(24px,3vw)]">
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
          <ul className="flex items-center gap-1">
            {NAV_KEYS.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  className="rounded-sm border border-border px-3.5 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:border-foreground/20 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2"
                >
                  {t(item.key)}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <MobileNav />
        <div className="hidden items-center gap-2 lg:flex">
          <CommandPalette />
          <LanguageSelector />
          <ThemeToggle />
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-8 items-center gap-1.5 rounded-sm border border-foreground px-3.5 text-sm font-medium transition-colors hover:bg-foreground hover:text-background focus-visible:outline-2 focus-visible:outline-offset-2"
          >
            {t('hero.github')}
            <ArrowUpRight className="size-3.5" aria-hidden="true" />
          </a>
        </div>
      </div>
    </header>
  )
}
