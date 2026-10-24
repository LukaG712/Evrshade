import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function NotFound() {
  return (
    <section className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background blueprint">
      <div className="relative z-10 mx-6 flex max-w-xl flex-col items-center text-center">
        <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
          Error 404
        </p>
        <h1 className="mt-6 text-balance text-7xl font-semibold leading-[0.9] tracking-[-0.05em] text-foreground md:text-9xl">
          Lost in the
          <br />
          network<span className="text-signal">.</span>
        </h1>
        <p className="mt-6 max-w-md text-pretty text-base leading-snug text-muted-foreground md:text-lg">
          This page doesn&apos;t exist yet. The service you&apos;re looking for may still be under development, or the link may have changed.
        </p>
        <div className="mt-10">
          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-sm border border-border px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted hover:border-foreground/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
          >
            <ArrowLeft className="size-4" />
            Back to home
          </Link>
        </div>
      </div>
    </section>
  )
}
