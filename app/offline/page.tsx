'use client'

export default function Offline() {
  return (
    <html>
      <body>
        <div className="flex min-h-svh flex-col items-center justify-center px-4 text-center">
          <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">Offline</p>
          <h1 className="mt-4 text-balance text-4xl font-semibold leading-[0.9] tracking-[-0.05em] md:text-6xl lg:text-7xl">
            No connection<span className="text-signal">.</span>
          </h1>
          <p className="mt-6 max-w-md text-pretty text-lg leading-snug text-muted-foreground">
            You&apos;re currently offline. The page you&apos;re looking for isn&apos;t available right now. Check your connection and try again.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="mt-8 inline-flex h-11 items-center gap-2 border border-foreground px-5 text-sm font-medium transition-colors hover:bg-foreground hover:text-background"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  )
}
