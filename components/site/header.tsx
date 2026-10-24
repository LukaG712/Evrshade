import { ArrowUpRight } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'
import { MobileNav } from './mobile-nav'
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

export function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-border bg-background/90 backdrop-blur-lg" style={{ paddingTop: 'env(safe-area-inset-top, 0)' }}>
      <div className="flex h-16 items-center justify-between px-6 md:px-[max(24px,3vw)]">
        {/* Logo */}
        <a href="#top" className="flex shrink-0 items-center gap-2.5 focus-visible:outline-2 focus-visible:outline-offset-4">
          <span className="grid size-5 grid-cols-2 gap-px" aria-hidden="true">
            <span className="bg-foreground" />
            <span className="bg-foreground" />
            <span className="bg-foreground" />
            <span className="bg-signal" />
          </span>
          <span className="text-base font-semibold tracking-tight">Evershade</span>
        </a>

        {/* Desktop Nav */}
        <nav aria-label="Primary" className="hidden lg:block">
          <ul className="flex items-center gap-1.5">
            {NAV.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  className="border border-border px-3.5 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:border-foreground/20 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2"
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        {/* Right side */}
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-8 items-center gap-1.5 border border-border px-3 text-sm font-medium text-muted-foreground transition-colors hover:border-foreground/20 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2"
          >
            GitHub
            <ArrowUpRight className="size-3.5" aria-hidden="true" />
          </a>
          <MobileNav />
        </div>
      </div>
    </header>
  )
}
