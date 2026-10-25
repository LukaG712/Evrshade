'use client'

import { useEffect, useState } from 'react'
import { Check, Lock, OctagonX, RotateCcw } from 'lucide-react'
import {
  AUTONOMY,
  HARDENING,
  INJECTION_RULES,
  ISOLATION,
  OPERATIONS,
  PANIC_STEPS,
  type AutonomyId,
} from '@/lib/evershade'
import { cn } from '@/lib/utils'
import { SectionHeading } from './section-heading'

const needsGate = (level: AutonomyId, sensitive: boolean) =>
  level === 'supervised' ? true : level === 'restricted' ? sensitive : false

export function Security() {
  return (
    <section id="security" aria-labelledby="security-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="security-title"
        label="Trust & control"
        title={
          <>
            Autonomy you can dial.
            <br />
            <span className="text-muted-foreground">A kill switch you can pull.</span>
          </>
        }
        lead="Agents act on real repositories with real credentials. Evershade puts approval gates, isolation boundaries and injection defenses between a model and a side effect."
      />

      <div className="mt-16 grid gap-px border border-foreground bg-foreground md:mt-24 lg:grid-cols-2">
        <AutonomyDial />
        <PanicPanel />
      </div>

      <div className="mt-px grid gap-px border border-t-0 border-foreground bg-foreground lg:grid-cols-2">
        <div className="bg-background p-5 md:p-8">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Slinker isolation levels'}</p>
          <ul className="mt-8 grid gap-4 sm:grid-cols-3">
            {ISOLATION.map((iso) => (
              <li key={iso.level} className="flex flex-col">
                <div className="relative grid aspect-square place-items-center border border-foreground/15">
                  {iso.strength >= 2 ? <span className="absolute inset-3 border-2 border-foreground" /> : null}
                  {iso.strength >= 1 ? <span className={cn('absolute border border-foreground', iso.strength >= 2 ? 'inset-7' : 'inset-5')} /> : null}
                  <span className={cn('relative size-3', iso.strength === 0 ? 'bg-destructive' : 'bg-signal')} />
                  <span className="absolute top-2 left-2 font-mono text-[10px] text-muted-foreground">{`L${iso.strength}`}</span>
                </div>
                <p className="mt-3 font-mono text-sm font-medium">{iso.level}</p>
                <p className="mt-1 text-sm leading-snug">{iso.boundary}</p>
                <p className="mt-1 text-sm leading-snug text-muted-foreground">{iso.use}</p>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-background p-5 md:p-8">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Prompt-injection defense'}</p>
          <p className="mt-6 text-pretty text-2xl font-semibold leading-tight tracking-tight md:text-3xl">
            Scraped pages, repo files, notes and tool output are <span className="text-signal-ink">data</span>, never
            instructions.
          </p>
          <ol className="mt-6 border-t border-foreground">
            {INJECTION_RULES.map((rule, i) => (
              <li key={rule} className="grid grid-cols-[2.5rem_1fr] gap-2 border-b border-border py-3 text-sm leading-snug">
                <span className="font-mono text-[11px] text-muted-foreground">{`R${i + 1}`}</span>
                {rule}
              </li>
            ))}
          </ol>
        </div>
      </div>

      {/* TODO(luka): Add links to SECURITY.md, prompt-injection test suite, and release signing verification. */}
      <div className="mt-12">
        <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Secure defaults'}</p>
        <ul className="mt-4 flex flex-wrap gap-2">
          {HARDENING.map((h) => (
            <li key={h} className="flex items-center gap-2 border border-foreground/20 px-2.5 py-1.5 font-mono text-[11px]">
              <span className="size-1.5 bg-signal" aria-hidden="true" />
              {h}
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}

function AutonomyDial() {
  const [level, setLevel] = useState<AutonomyId>('restricted')
  const current = AUTONOMY.find((a) => a.id === level)!
  const gated = OPERATIONS.filter((o) => needsGate(level, o.sensitive)).length

  return (
    <div className="bg-background p-5 md:p-8">
      <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Autonomy levels'}</p>
      <div role="radiogroup" aria-label="Autonomy level" className="mt-6 grid grid-cols-3 border border-foreground">
        {AUTONOMY.map((a, i) => {
          const on = a.id === level
          return (
            <button
              key={a.id}
              type="button"
              role="radio"
              aria-checked={on}
              onClick={() => setLevel(a.id)}
              className={cn(
                'flex flex-col items-start gap-3 border-r border-foreground p-3 text-left transition-colors last:border-r-0 md:p-4',
                on ? 'bg-foreground text-background' : 'hover:bg-foreground/5',
              )}
            >
              <span className="flex gap-0.5" aria-hidden="true">
                {[0, 1, 2].map((b) => (
                  <span key={b} className={cn('h-3 w-1.5', b <= i ? (on ? 'bg-signal' : 'bg-foreground') : 'bg-current/20')} />
                ))}
              </span>
              <span className="text-sm font-semibold leading-tight md:text-base">{a.name}</span>
            </button>
          )
        })}
      </div>
      <p className="mt-4 text-lg leading-snug">
        {current.rule}{' '}
        <span className="text-muted-foreground">{`${gated} of ${OPERATIONS.length} example operations gated.`}</span>
      </p>
      <ul className="mt-6 border-t border-foreground">
        {OPERATIONS.map((o) => {
          const gate = needsGate(level, o.sensitive)
          return (
            <li key={o.op} className="flex items-center justify-between gap-4 border-b border-border py-2.5">
              <span className="text-sm">{o.op}</span>
              <span
                className={cn(
                  'inline-flex min-w-24 items-center justify-center gap-1.5 px-2 py-1 font-mono text-[10px] uppercase tracking-wider transition-colors duration-300',
                  gate ? 'bg-foreground text-background' : 'border border-signal text-signal-ink',
                )}
              >
                {gate ? <Lock className="size-3" aria-hidden="true" /> : <Check className="size-3" aria-hidden="true" />}
                {gate ? 'Approval' : 'Auto'}
              </span>
            </li>
          )
        })}
      </ul>
      <p className="mt-4 font-mono text-[11px] text-muted-foreground">
        {'Level rules from the docs. Which operations count as sensitive is an example.'}
      </p>
    </div>
  )
}

function PanicPanel() {
  const [stage, setStage] = useState(-1)
  const engaged = stage >= 0
  const done = stage >= PANIC_STEPS.length

  useEffect(() => {
    if (!engaged || done) return
    const id = window.setTimeout(() => setStage((s) => s + 1), 550)
    return () => window.clearTimeout(id)
  }, [engaged, done, stage])

  return (
    <div className={cn('flex flex-col p-5 transition-colors duration-500 md:p-8', engaged ? 'bg-foreground text-background' : 'bg-background')}>
      <p className={cn('font-mono text-[11px] uppercase tracking-wider', engaged ? 'text-signal' : 'text-signal-ink')}>
        {'Emergency stop'}
      </p>
      <p className="mt-6 text-4xl font-semibold leading-[0.95] tracking-[-0.04em] md:text-5xl">
        {done ? 'Everything is stopped.' : engaged ? 'Stopping…' : 'One command halts it all.'}
      </p>
      <code className="mt-4 font-mono text-sm opacity-70">{'$ evershade panic'}</code>

      <ol className="mt-8 flex-1 border-t border-current/20" aria-live="polite">
        {PANIC_STEPS.map((s, i) => {
          const hit = stage > i
          return (
            <li key={s} className={cn('flex items-center gap-3 border-b border-current/15 py-2.5 text-sm transition-opacity duration-300', hit ? 'opacity-100' : 'opacity-40')}>
              <span className={cn('grid size-4 shrink-0 place-items-center', hit ? 'bg-signal text-foreground' : 'border border-current/40')}>
                {hit ? <Check className="size-3" aria-hidden="true" /> : null}
              </span>
              {s}
            </li>
          )
        })}
      </ol>

      <div className="mt-6 flex items-center gap-3">
        {done ? (
          <button
            type="button"
            onClick={() => setStage(-1)}
            className="inline-flex h-11 items-center gap-2 border border-background px-5 text-sm font-medium transition-colors hover:bg-background hover:text-foreground"
          >
            <RotateCcw className="size-4" aria-hidden="true" />
            Reverse deliberately
          </button>
        ) : (
          <button
            type="button"
            disabled={engaged}
            onClick={() => setStage(0)}
            className="inline-flex h-11 items-center gap-2 bg-destructive px-5 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            <OctagonX className="size-4" aria-hidden="true" />
            Pull the kill switch
          </button>
        )}
        <span className="font-mono text-[11px] opacity-60">{'Simulation'}</span>
      </div>
    </div>
  )
}
