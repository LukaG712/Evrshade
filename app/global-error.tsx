'use client'

import { ArrowLeft } from 'lucide-react'

export default function GlobalError() {
  return (
    <html>
      <body>
        <div className="blueprint flex min-h-svh flex-col items-center justify-center px-4 text-center">
          <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">500</p>
          <h1 className="mt-4 text-balance text-4xl font-semibold leading-[0.9] tracking-[-0.05em] md:text-6xl lg:text-7xl">
            Something broke<span className="text-signal">.</span>
          </h1>
          <p className="mt-6 max-w-md text-pretty text-lg leading-snug text-muted-foreground">
            A server error occurred. Our agents are investigating the incident.
          </p>
          <a
            href="#top"
            className="mt-8 inline-flex h-11 items-center gap-2 border border-foreground px-5 text-sm font-medium transition-colors hover:bg-foreground hover:text-background"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to home
          </a>
        </div>
      </body>
    </html>
  )
}
