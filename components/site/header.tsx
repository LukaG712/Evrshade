'use client'

import { useI18n } from '@/lib/i18n'
import { MobileNav } from './mobile-nav'

const NAV_LINKS = [
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
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 lg:h-16 lg:px-[max(24px,3vw)]">
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
            {NAV_LINKS.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  className="rounded-sm border border-border px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:border-foreground/20 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2"
                >
                  {t(item.key)}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <div className="flex items-center gap-2">
          <MobileNav />
        </div>
      </div>
    </header>
  )
}
