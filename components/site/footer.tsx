import { ArrowUpRight } from 'lucide-react'
import { REPO_URL, SERVICES, VERSION } from '@/lib/evershade'
import { BuildStatus } from './build-status'

export function Footer() {
  return (
    <footer className="mt-32 overflow-hidden border-t border-foreground px-4 pb-20 pt-16 md:mt-48 md:pb-16 md:px-[max(24px,3vw)]">
      <div className="grid gap-10 md:grid-cols-12">
        {/* Brand */}
        <div className="md:col-span-4">
          <a href="#top" className="flex items-center gap-2.5">
            <span className="grid size-5 grid-cols-2 gap-px" aria-hidden="true">
              <span className="bg-foreground" />
              <span className="bg-foreground" />
              <span className="bg-foreground" />
              <span className="bg-signal" />
            </span>
            <span className="text-sm font-semibold tracking-tight">Evershade</span>
          </a>
          <p className="mt-4 max-w-xs text-pretty text-sm leading-snug text-muted-foreground">
            You own everything. Nothing leaves your machine unless you explicitly connect an external AI provider.
          </p>
        </div>

        {/* Navigation */}
        <div className="md:col-span-2">
          <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">Navigation</p>
          <ul className="mt-4 space-y-2">
            {['Overview', 'How It Works', 'Platform', 'Get Started', 'About', 'Roadmap', 'Blog', 'Compare'].map((label) => {
              const isPage = label === 'Blog' || label === 'Compare'
              const href = isPage ? `/${label.toLowerCase()}` : `#${label.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z-]/g, '')}`
              return (
                <li key={label}>
                  <a href={href} className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                    {label}
                  </a>
                </li>
              )
            })}
          </ul>
        </div>

        {/* Resources */}
        <div className="md:col-span-3">
          <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">Resources</p>
          <ul className="mt-4 space-y-2">
            {[
              ['Repository', REPO_URL],
              ['Changelog', `${REPO_URL}/blob/main/CHANGELOG.md`],
              ['Roadmap', `${REPO_URL}/blob/main/ROADMAP.md`],
              ['Documentation', `${REPO_URL}/tree/main/docs`],
            ].map(([label, href]) => (
              <li key={label as string}>
                <a href={href as string} target="_blank" rel="noreferrer" className="group inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-signal-ink">
                  {label}
                  <ArrowUpRight className="size-3.5 opacity-40 transition-opacity group-hover:opacity-100" aria-hidden="true" />
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Platform */}
        <div className="md:col-span-3">
          <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">Platform</p>
          <div className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2">
            {SERVICES.map((svc) => (
              <span key={svc.id} className="text-sm text-muted-foreground">
                {svc.name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="mt-16 flex items-center justify-between border-t border-border pt-6 font-mono text-[11px] text-muted-foreground">
        <div className="flex items-center gap-3">
          <span>{`v${VERSION}`}</span>
          <BuildStatus />
        </div>
        <span>MIT License · Self-hosted · Docker</span>
      </div>

      <p
        aria-hidden="true"
        className="mt-16 select-none text-foreground/5 font-semibold leading-[0.75] tracking-[-0.075em]"
        style={{ fontSize: 'clamp(4.5rem, 21.5vw, 26rem)' }}
      >
        Evershade<span className="text-signal">.</span>
      </p>
    </footer>
  )
}
