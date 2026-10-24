import { SectionHeading } from './section-heading'

export function Download() {
  return (
    <section id="download" aria-labelledby="download-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="download-title"
        label="Download"
        title={
          <>Get started<span className="text-signal">.</span></>
        }
        lead="Use the install one-liner and download dropdown above, or skip straight to Docker Compose."
      />

      <div className="mt-12 grid gap-10 md:mt-16 md:grid-cols-12">
        {/* Quick info */}
        <div className="md:col-span-5">
          <div className="border border-border p-5">
            <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'What gets installed'}</p>
            <ul className="mt-4 space-y-3 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/40" aria-hidden="true" />
                The <code className="font-mono text-xs">evershade</code> CLI binary
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/40" aria-hidden="true" />
                Docker Compose profiles (minimal, standard, full)
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/40" aria-hidden="true" />
                Default <code className="font-mono text-xs">.env</code> configuration
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-foreground/40" aria-hidden="true" />
                Shell completion for bash, zsh, and PowerShell
              </li>
            </ul>
          </div>
        </div>

        <div className="md:col-span-4 md:col-start-8">
          <div className="rounded border border-dashed border-foreground/50 p-5">
            <p className="text-sm font-semibold tracking-tight">Prefer Docker only?</p>
            <p className="mt-2 text-sm text-muted-foreground">
              Skip the binary and go straight to{' '}
              <a href="#docker" className="text-signal-ink underline underline-offset-4">
                Docker Compose
              </a>{' '}
              with the one-liner above.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
