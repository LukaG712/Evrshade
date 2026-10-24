'use client'

import { useEffect, useRef, useState } from 'react'
import { cn } from '@/lib/utils'
import { SectionHeading } from './section-heading'

const LANES = ['Speedy', 'Slammer', 'Greenie', 'Shrewd', 'Gobber', 'Hider', 'Slinker', 'Trapper', 'Sneaker', 'Poltergeist']
const L = (name: string) => LANES.indexOf(name)

const STEPS = [
  { from: 'Speedy', to: 'Greenie', call: 'POST /api/missions', body: 'Bearer token verified. Idempotency key recorded so retries never double-run.' },
  { from: 'Greenie', to: 'Gobber', call: 'hybrid search', body: 'Semantic + keyword retrieval over the knowledge graph, scoped to user and project.' },
  { from: 'Greenie', to: 'Shrewd', call: 'plan', body: 'Model routing chooses a provider by cost and privacy classification.' },
  { from: 'Greenie', to: 'Hider', call: 'lease secret', body: 'AES-256-GCM at rest. Values are redacted from logs and model context.' },
  { from: 'Greenie', to: 'Slinker', call: 'dispatch feature', body: 'Parallel workers run inside isolated containers or workstations.' },
  { from: 'Greenie', to: 'Trapper', call: 'fetch docs', body: 'SSRF-guarded crawl. Scraped pages are treated as data, never instructions.' },
  { from: 'Slinker', to: 'Greenie', call: 'diff + results', body: 'Output is checked against the validation contract before anything ships.' },
  { from: 'Greenie', to: 'Sneaker', call: 'OTLP spans', body: 'Metrics, traces and logs for every step, with secrets redacted.' },
  { from: 'Greenie', to: 'Poltergeist', call: 'notify', body: 'Slack, Discord, email or Telegram when a milestone lands or a gate opens.' },
  { from: 'Greenie', to: 'Slammer', call: 'SSE stream', body: 'Every event streams to the dashboard in real time.' },
]

export function RequestTrace() {
  const ref = useRef<HTMLDivElement>(null)
  const [active, setActive] = useState(0)
  const [auto, setAuto] = useState(true)
  const [inView, setInView] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(([e]) => setInView(e.isIntersecting), { threshold: 0.3 })
    io.observe(el)
    return () => io.disconnect()
  }, [])

  useEffect(() => {
    if (!auto || !inView) return
    const id = window.setInterval(() => setActive((a) => (a + 1) % STEPS.length), 1900)
    return () => window.clearInterval(id)
  }, [auto, inView])

  const pick = (i: number) => {
    setAuto(false)
    setActive(i)
  }

  const step = STEPS[active]
  const N = LANES.length

  return (
    <section id="trace" aria-labelledby="trace-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="trace-title"
        label="Anatomy of a feature"
        title={
          <>
            Follow one feature
            <br />
            <span className="text-muted-foreground">through the platform.</span>
          </>
        }
        lead="Greenie owns the conversation. Every other service does one job over HTTP. Pick a step to see who talks to whom and why."
      />

      <div ref={ref} className="mt-16 grid gap-6 md:mt-24 lg:grid-cols-12">
        <div className="overflow-x-auto border border-foreground lg:col-span-8">
          <div className="relative min-w-[860px]">
            <div className="grid border-b border-foreground" style={{ gridTemplateColumns: `repeat(${N}, 1fr)` }}>
              {LANES.map((lane) => {
                const on = lane === step.from || lane === step.to
                return (
                  <div
                    key={lane}
                    className={cn(
                      'border-r border-border px-1 py-3 text-center font-mono text-[10px] uppercase tracking-wider transition-colors duration-300 last:border-r-0',
                      on ? 'bg-foreground text-background' : 'text-muted-foreground',
                    )}
                  >
                    {lane}
                  </div>
                )
              })}
            </div>

            <div className="relative">
              <div className="pointer-events-none absolute inset-0 grid" style={{ gridTemplateColumns: `repeat(${N}, 1fr)` }} aria-hidden="true">
                {LANES.map((lane) => (
                  <div key={lane} className="flex justify-center">
                    <div className="w-px bg-foreground/10" />
                  </div>
                ))}
              </div>

              <ol aria-label="Request sequence">
                {STEPS.map((s, i) => {
                  const a = L(s.from)
                  const b = L(s.to)
                  const lo = Math.min(a, b)
                  const hi = Math.max(a, b)
                  const isActive = i === active
                  const right = b > a
                  return (
                    <li key={s.call} className="relative h-11">
                      <button
                        type="button"
                        onClick={() => pick(i)}
                        aria-current={isActive ? 'step' : undefined}
                        aria-label={`Step ${i + 1}: ${s.from} to ${s.to}, ${s.call}`}
                        className="absolute inset-0 w-full"
                      />
                      <div
                        className="pointer-events-none absolute top-1/2"
                        style={{ left: `${((lo + 0.5) / N) * 100}%`, width: `${((hi - lo) / N) * 100}%` }}
                        aria-hidden="true"
                      >
                        <div
                          className={cn(
                            'relative h-px transition-colors duration-300',
                            isActive ? 'bg-signal' : i < active ? 'bg-foreground/50' : 'bg-foreground/15',
                          )}
                        >
                          <span
                            className={cn(
                              'absolute top-1/2 size-1.5 -translate-y-1/2 transition-colors duration-300',
                              right ? '-right-0.5' : '-left-0.5',
                              isActive ? 'bg-signal' : i < active ? 'bg-foreground/50' : 'bg-foreground/15',
                            )}
                          />
                          {isActive ? (
                            <span
                              key={active}
                              className="absolute top-1/2 size-2 -translate-y-1/2 bg-signal"
                              style={{ animation: `${right ? 'travel-r' : 'travel-l'} 1.2s cubic-bezier(.6,0,.2,1) infinite` }}
                            />
                          ) : null}
                        </div>
                        <span
                          className={cn(
                            'absolute -top-4 left-1/2 -translate-x-1/2 whitespace-nowrap bg-background px-1.5 font-mono text-[10px] transition-colors duration-300',
                            isActive ? 'text-foreground' : 'text-muted-foreground/70',
                          )}
                        >
                          {`${String(i + 1).padStart(2, '0')} ${s.call}`}
                        </span>
                      </div>
                    </li>
                  )
                })}
              </ol>
            </div>
          </div>
        </div>

        <div className="flex flex-col lg:col-span-4" aria-live="polite">
          <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
            {`Step ${String(active + 1).padStart(2, '0')} / ${String(STEPS.length).padStart(2, '0')}`}
          </p>
          <p key={active} className="mt-4 text-4xl font-semibold leading-[0.95] tracking-[-0.04em] animate-in fade-in slide-in-from-bottom-2 duration-500 md:text-5xl">
            {step.from}
            <span className="text-signal">{' → '}</span>
            {step.to}
          </p>
          <code className="mt-5 inline-flex w-fit items-center gap-2 border border-foreground px-3 py-2 font-mono text-xs">
            <span className="size-1.5 bg-signal" aria-hidden="true" />
            {step.call}
          </code>
          <p className="mt-5 max-w-sm text-pretty text-lg leading-snug">{step.body}</p>

          <div className="mt-8 flex flex-wrap items-center gap-2 lg:mt-auto">
            <button
              type="button"
              onClick={() => pick((active - 1 + STEPS.length) % STEPS.length)}
              className="h-9 border border-foreground px-3 font-mono text-[11px] uppercase tracking-wider transition-colors hover:bg-foreground hover:text-background"
            >
              Prev
            </button>
            <button
              type="button"
              onClick={() => pick((active + 1) % STEPS.length)}
              className="h-9 border border-foreground px-3 font-mono text-[11px] uppercase tracking-wider transition-colors hover:bg-foreground hover:text-background"
            >
              Next
            </button>
            <button
              type="button"
              onClick={() => setAuto((a) => !a)}
              aria-pressed={auto}
              className={cn(
                'h-9 px-3 font-mono text-[11px] uppercase tracking-wider transition-colors',
                auto ? 'bg-foreground text-background' : 'border border-foreground/30 text-muted-foreground hover:border-foreground',
              )}
            >
              {auto ? 'Auto · on' : 'Auto · off'}
            </button>
          </div>
          <p className="mt-6 font-mono text-[11px] leading-relaxed text-muted-foreground">
            {'Illustrative sequence derived from the service dependency graph in version-manifest.json.'}
          </p>
        </div>
      </div>
    </section>
  )
}
