export function ChangelogTicker() {
  return (
    <section id="changelog" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <div className="grid gap-10 md:grid-cols-12">
        <div className="md:col-span-7">
          <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Current status'}</p>
          <h2 className="mt-4 text-4xl font-semibold leading-[0.9] tracking-[-0.05em] text-balance md:text-6xl lg:text-7xl">
            Under development<span className="text-signal">.</span>
          </h2>
          <p className="mt-6 max-w-2xl text-pretty text-lg leading-snug text-muted-foreground">
            Evershade is under active development. Check the repo for the latest changes and open items.
          </p>

          <div className="mt-10 border border-foreground p-5">
            <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Current focus'}</p>
            <ul className="mt-4 space-y-2">
              {[
                'Core microservices: Greenie, Slinker, Trapper, Gobber',
                'Agent harness with spec mode and isolation',
                'Observability with Sneaker metrics and traces',
                'Speedy CLI and Slammer dashboard',
                'Docker Compose profiles for quick setup',
              ].map((change) => (
                <li key={change} className="flex items-start gap-2 text-sm leading-snug">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-signal-ink" />
                  {change}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}
