import { ArrowUpRight } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'

const NAV_LINKS = [
  { href: '#overview', label: 'Overview' },
  { href: '#how-it-works', label: 'How It Works' },
  { href: '#platform', label: 'Platform' },
  { href: '#get-started', label: 'Get Started' },
  { href: '#about', label: 'About' },
  { href: '#roadmap', label: 'Roadmap' },
]

const RESOURCE_LINKS = [
  { label: 'Repository', href: REPO_URL, external: true },
  { label: 'Documentation', href: `${REPO_URL}/tree/master/docs`, external: true },
  { label: 'Changelog', href: `${REPO_URL}/blob/master/CHANGELOG.md`, external: true },
  { label: 'Roadmap', href: `${REPO_URL}/blob/master/ROADMAP.md`, external: true },
]

const PLATFORM_LINKS = [
  { label: 'Greenie', href: '#services' },
  { label: 'Slinker', href: '#services' },
  { label: 'Trapper', href: '#services' },
  { label: 'Gobber', href: '#services' },
  { label: 'Slammer', href: '#services' },
  { label: 'Speedy CLI', href: '#services' },
]

export function Footer() {
  return (
    <footer className="mt-24 border-t border-border px-4 pt-16 md:mt-48 md:px-[max(24px,3vw)]">
      <div className="grid gap-10 sm:grid-cols-2 md:grid-cols-12 lg:gap-12">
        {/* Brand column */}
        <div className="sm:col-span-2 md:col-span-4">
          <a href="#top" className="flex items-center gap-2.5">
            <span className="grid size-5 grid-cols-2 gap-px" aria-hidden="true">
              <span className="bg-foreground" />
              <span className="bg-foreground" />
              <span className="bg-foreground" />
              <span className="bg-transparent" />
            </span>
            <span className="text-sm font-semibold tracking-tight">Evershade</span>
          </a>
          <p className="mt-4 max-w-xs text-pretty text-sm leading-relaxed text-muted-foreground">
            A self-hosted AI agent platform. Your agents. Your hardware. Your data.
          </p>
        </div>

        {/* Navigation */}
        <div className="sm:col-span-1 md:col-span-2">
          <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{'Navigation'}</p>
          <ul className="mt-4 space-y-2.5">
            {NAV_LINKS.map((item) => (
              <li key={item.href}>
                <a href={item.href} className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Resources */}
        <div className="sm:col-span-1 md:col-span-2">
          <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{'Resources'}</p>
          <ul className="mt-4 space-y-2.5">
            {RESOURCE_LINKS.map((item) => (
              <li key={item.label}>
                <a
                  href={item.href}
                  { ...(item.external ? { target: '_blank' as const, rel: 'noreferrer' } : {}) }
                  className="group inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
                >
                  {item.label}
                  {item.external && (
                    <ArrowUpRight className="size-3 opacity-40 transition-opacity group-hover:opacity-100" aria-hidden="true" />
                  )}
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Platform */}
        <div className="sm:col-span-2 md:col-span-4">
          <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{'Platform'}</p>
          <ul className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2.5">
            {PLATFORM_LINKS.map((item) => (
              <li key={item.label}>
                <a href={item.href} className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="mt-16 flex flex-col items-start justify-between gap-4 border-t border-border pt-6 md:flex-row md:items-center">
        <p className="text-xs text-muted-foreground">
          {new Date().getFullYear()} Evershade. MIT License.
        </p>
        <p className="text-xs text-muted-foreground">
          Self-hosted &middot; Docker &middot; Open source
        </p>
      </div>

      {/* Background watermark */}
      <p
        aria-hidden="true"
        className="relative -z-10 mt-12 select-none font-semibold leading-[0.75] tracking-[-0.075em] text-foreground/5"
        style={{ fontSize: 'clamp(4.5rem, 21.5vw, 26rem)' }}
      >
        Evershade<span className="text-signal">.</span>
      </p>
    </footer>
  )
}
