'use client'

import { memo, useEffect, useMemo, useRef, useState } from 'react'
import { Check, CircleDashed, Loader, Lock, Pause, Play, RotateCcw, ShieldCheck, X } from 'lucide-react'
import {
  APPROVE_TAIL,
  CHECKS,
  GATE,
  MILESTONES,
  MISSION,
  REJECT_TAIL,
  SCRIPT,
  type CheckId,
  type CheckStatus,
  type FeatureStatus,
  type LogLevel,
  type MissionEvent,
} from '@/lib/mission-script'
import { cn } from '@/lib/utils'
import { SectionHeading } from './section-heading'

type Decision = null | 'approved' | 'rejected'
type LogLine = { t: number; svc: string; text: string; level: LogLevel }

const GATE_INDEX = SCRIPT.findIndex((e) => e.type === 'gate')

function derive(events: MissionEvent[]) {
  const features: Record<string, { status: FeatureStatus; worker?: number }> = {}
  MILESTONES.forEach((m) => m.features.forEach((f) => (features[f.id] = { status: f.initial })))
  const checks: Record<CheckId, CheckStatus> = { tests: 'idle', lint: 'idle', types: 'idle', security: 'idle' }
  const logs: LogLine[] = []
  let phase = 'Queued'
  let clock = 0
  let retries = 0

  for (const e of events) {
    clock += e.d
    if (e.type === 'phase') {
      phase = e.phase
      if (e.phase === 'Fix-revalidate') retries += 1
    } else if (e.type === 'log') logs.push({ t: clock, svc: e.svc, text: e.text, level: e.level ?? 'info' })
    else if (e.type === 'feature') features[e.id] = { status: e.status, worker: e.worker ?? features[e.id].worker }
    else if (e.type === 'check') checks[e.id] = e.status
  }
  return { features, checks, logs, phase, clock, retries }
}

const fmt = (ms: number) => {
  const s = Math.floor((ms * 9) / 1000)
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
}

export function MissionConsole() {
  const rootRef = useRef<HTMLDivElement>(null)
  const [step, setStep] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [started, setStarted] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [decision, setDecision] = useState<Decision>(null)

  const script = useMemo(() => {
    if (!decision) return SCRIPT
    return [...SCRIPT, ...(decision === 'approved' ? APPROVE_TAIL : REJECT_TAIL)]
  }, [decision])

  const atGate = step > GATE_INDEX && decision === null
  const finished = step >= script.length && decision !== null
  const state = useMemo(() => derive(script.slice(0, step)), [script, step])

  useEffect(() => {
    const el = rootRef.current
    if (!el || started) return
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setStarted(true)
          setPlaying(true)
          io.disconnect()
        }
      },
      { threshold: 0.35 },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [started])

  useEffect(() => {
    if (!playing || atGate || step >= script.length) return
    const id = window.setTimeout(() => setStep((s) => s + 1), script[step].d / speed)
    return () => window.clearTimeout(id)
  }, [playing, atGate, step, script, speed])

  // Logs are displayed in a fixed-height overflow-hidden container; no auto-scroll needed.

  const replay = () => {
    setDecision(null)
    setStep(0)
    setPlaying(true)
    setStarted(true)
  }

  const allFeatures = MILESTONES.flatMap((m) => m.features)
  const visible = allFeatures.filter((f) => state.features[f.id].status !== 'hidden')
  const doneCount = visible.filter((f) => state.features[f.id].status === 'done').length
  const lanes = [1, 2, 3].map((w) => {
    const f = allFeatures.find((x) => state.features[x.id].status === 'running' && state.features[x.id].worker === w)
    return { w, feature: f }
  })

  return (
    <section id="console" aria-labelledby="console-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="console-title"
        label="Mission Console"
        title={
          <>
            One prompt.
            <br />
            <span className="text-muted-foreground">Ten services at work.</span>
          </>
        }
        lead="A replay of a mission in Slammer, the Evershade dashboard. Greenie plans with Shrewd and pulls context from Gobber. It fans features out to Slinker workers, validates against a contract, fixes its own failures, then stops at your approval gate."
      />

      <div ref={rootRef} className="mt-16 border border-foreground bg-background md:mt-24">
        {/* Window chrome */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-foreground px-3 py-2.5 md:px-4">
          <div className="flex min-w-0 items-center gap-3 font-mono text-[11px] uppercase tracking-wider">
            <span className="grid size-4 shrink-0 grid-cols-2 gap-px" aria-hidden="true">
              <span className="bg-foreground" />
              <span className="bg-foreground" />
              <span className="bg-foreground" />
              <span className="bg-signal" />
            </span>
            <span className="font-semibold">Mission Console</span>
            <span className="truncate text-muted-foreground">{`replay / ${MISSION.id}`}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="mr-2 hidden border border-dashed border-foreground/50 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground sm:inline">
              Simulated replay
            </span>
            <ConsoleButton
              label={playing ? 'Pause replay' : 'Play replay'}
              onClick={() => (finished ? replay() : setPlaying((p) => !p))}
            >
              {playing && !finished ? <Pause className="size-3.5" /> : <Play className="size-3.5" />}
            </ConsoleButton>
            <ConsoleButton label="Restart replay" onClick={replay}>
              <RotateCcw className="size-3.5" />
            </ConsoleButton>
            <button
              type="button"
              onClick={() => setSpeed((s) => (s === 1 ? 2 : s === 2 ? 4 : 1))}
              className="h-7 min-w-10 border border-foreground/20 px-2 font-mono text-[11px] tabular-nums transition-colors hover:border-foreground"
              aria-label={`Playback speed ${speed}x`}
            >
              {`${speed}×`}
            </button>
          </div>
        </div>

        {/* Mission header */}
        <div className="grid gap-4 border-b border-foreground p-4 md:grid-cols-12 md:items-end md:p-6">
          <div className="md:col-span-7">
            <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
              {`${MISSION.id} · ${MISSION.repo} · ${MISSION.branch}`}
            </p>
            <h3 className="mt-2 text-balance text-2xl font-semibold leading-tight tracking-tight md:text-4xl">
              {MISSION.title}
            </h3>
          </div>
          <dl className="grid grid-cols-2 gap-px border border-foreground/15 bg-foreground/15 sm:grid-cols-4 md:col-span-5">
            <Stat label="Status">
              <span className="flex items-center gap-1.5" aria-live="polite">
                <StatusDot phase={state.phase} />
                {state.phase}
              </span>
            </Stat>
            <Stat label="Autonomy">Restricted</Stat>
            <Stat label="Elapsed">
              <span className="tabular-nums">{fmt(state.clock)}</span>
            </Stat>
            <Stat label="Retries">
              <span className="tabular-nums">{`${state.retries} / 2`}</span>
            </Stat>
          </dl>
        </div>

        {atGate || decision ? (
          <ApprovalBand
            decision={decision}
            onApprove={() => setDecision('approved')}
            onReject={() => setDecision('rejected')}
          />
        ) : null}

        <div className="grid md:grid-cols-12">
          {/* Milestones */}
          <div className="border-b border-foreground md:col-span-4 md:border-r md:border-b-0">
            <PanelTitle left="Milestones" right={`${doneCount}/${visible.length} features`} />
            <ol className="p-2">
              {MILESTONES.map((m) => (
                <li key={m.id} className="py-1.5">
                  <p className="flex items-center gap-2 px-2 py-1 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                    <span className="text-foreground">{m.id}</span>
                    {m.title}
                  </p>
                  <ul>
                    {m.features
                      .filter((f) => state.features[f.id].status !== 'hidden')
                      .map((f) => {
                        const fs = state.features[f.id]
                        return (
                          <li
                            key={f.id}
                            className={cn(
                              'flex items-center gap-2.5 px-2 py-1.5 text-sm transition-colors duration-300 animate-in fade-in',
                              fs.status === 'running' && 'bg-foreground/[0.04]',
                              fs.status === 'queued' && 'text-foreground/40',
                            )}
                          >
                            <FeatureIcon status={fs.status} />
                            <span className="font-mono text-[11px] text-muted-foreground">{f.id}</span>
                            <span className={cn('flex-1 truncate', f.id === 'F2.4' && 'italic')}>{f.title}</span>
                            {fs.status === 'running' && fs.worker ? (
                              <span className="font-mono text-[10px] text-signal-ink">{`w${fs.worker}`}</span>
                            ) : null}
                          </li>
                        )
                      })}
                  </ul>
                </li>
              ))}
            </ol>
          </div>

          {/* Log stream */}
          <div className="flex min-w-0 flex-col border-b border-foreground md:col-span-5 md:border-r md:border-b-0">
            <PanelTitle left="GET /logs/stream" right="SSE" live={playing && !finished && !atGate} />
            <ol
              className="h-72 overflow-hidden p-3 font-mono text-[11px] leading-relaxed md:h-[26rem] md:p-4 md:text-xs"
              aria-label="Mission log"
            >
              {state.logs.length === 0 ? (
                <li className="text-muted-foreground">{'Waiting for mission events…'}</li>
              ) : null}
              {state.logs.map((l, i) => (
                <li key={i} className="grid grid-cols-[3.25rem_5.5rem_1fr] gap-2 animate-in fade-in slide-in-from-bottom-1 duration-300">
                  <span className="tabular-nums text-muted-foreground">{fmt(l.t)}</span>
                  <span className="truncate uppercase text-foreground/60">{l.svc}</span>
                  <span
                    className={cn(
                      'break-words',
                      l.level === 'ok' && 'text-signal-ink',
                      l.level === 'err' && 'text-destructive',
                      l.level === 'warn' && 'font-semibold',
                    )}
                  >
                    {l.text}
                  </span>
                </li>
              ))}
            </ol>
          </div>

          {/* Validation + workers */}
          <div className="md:col-span-3">
            <PanelTitle left="Validation contract" />
            <ul className="border-b border-foreground">
              {CHECKS.map((c) => {
                const s = state.checks[c.id]
                return (
                  <li key={c.id} className="flex items-center justify-between gap-3 border-b border-border px-4 py-3 last:border-b-0">
                    <div className="min-w-0">
                      <p className="text-sm font-medium">{c.label}</p>
                      <p className="truncate font-mono text-[10px] text-muted-foreground">{c.cmd}</p>
                    </div>
                    <CheckBadge status={s} />
                  </li>
                )
              })}
            </ul>
            <PanelTitle left="Workers" right="Slinker" />
            <ul className="p-2">
              {lanes.map(({ w, feature }) => (
                <li key={w} className="flex items-center gap-3 px-2 py-2">
                  <span
                    className={cn(
                      'grid size-6 shrink-0 place-items-center border font-mono text-[10px] transition-colors',
                      feature ? 'border-foreground bg-foreground text-background' : 'border-foreground/20 text-foreground/40',
                    )}
                  >
                    {`w${w}`}
                  </span>
                  <span className={cn('min-w-0 flex-1 truncate text-sm', !feature && 'text-muted-foreground')}>
                    {feature ? feature.title : 'idle'}
                  </span>
                  {feature ? <span className="h-1 w-8 overflow-hidden bg-foreground/10"><span className="block h-full w-1/2 animate-[scan_1.1s_ease-in-out_infinite] bg-signal" /></span> : null}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="h-1 bg-foreground/10" aria-hidden="true">
          <div
            className="h-full bg-signal transition-[width] duration-500"
            style={{ width: `${(doneCount / Math.max(1, visible.length)) * 100}%` }}
          />
        </div>
      </div>

      <p className="mt-4 max-w-3xl font-mono text-[11px] leading-relaxed text-muted-foreground">
        {
          'Illustrative replay built on the real mission model: milestones, features, parallel workers, a validation contract, fix-revalidate with configurable retries, approval gates and SSE log streaming. Repository, timings and output are examples.'
        }
      </p>
    </section>
  )
}

const ApprovalBand = memo(({
  decision,
  onApprove,
  onReject,
}: {
  decision: Decision
  onApprove: () => void
  onReject: () => void
}) => {
  return (
    <div
      role="region"
      aria-label="Approval gate"
      aria-live="assertive"
      className={cn(
        'flex flex-col gap-4 border-b border-foreground p-4 animate-in fade-in slide-in-from-top-2 md:flex-row md:items-center md:justify-between md:p-5',
        decision === null ? 'bg-foreground text-background' : 'bg-background',
      )}
    >
      <div className="flex min-w-0 items-start gap-3">
        <span
          className={cn(
            'mt-0.5 grid size-7 shrink-0 place-items-center',
            decision === null ? 'bg-signal text-foreground' : 'border border-foreground',
          )}
        >
          {decision === 'approved' ? <Check className="size-4" /> : decision === 'rejected' ? <X className="size-4" /> : <Lock className="size-3.5" />}
        </span>
        <div className="min-w-0">
          <p className="font-mono text-[11px] uppercase tracking-wider opacity-70">
            {decision === null ? `Approval required · ${GATE.actor}` : decision === 'approved' ? 'Approved by you' : 'Rejected by you'}
          </p>
          <code className="mt-1 block break-words font-mono text-sm md:text-base">{GATE.action}</code>
          <p className="mt-1 text-sm opacity-70">{GATE.reason}</p>
        </div>
      </div>
      {decision === null ? (
        <div className="flex shrink-0 gap-2">
          <button
            type="button"
            onClick={onReject}
            className="h-10 border border-background/40 px-4 text-sm font-medium transition-colors hover:bg-background hover:text-foreground"
          >
            Reject
          </button>
          <button
            type="button"
            onClick={onApprove}
            className="inline-flex h-10 items-center gap-2 bg-signal px-4 text-sm font-medium text-foreground transition-colors hover:bg-background"
          >
            <ShieldCheck className="size-4" aria-hidden="true" />
            Approve
          </button>
        </div>
      ) : null}
    </div>
  )
})

const ConsoleButton = memo(({ label, onClick, children }: { label: string; onClick: () => void; children: React.ReactNode }) => (
  <button
    type="button"
    onClick={onClick}
    aria-label={label}
    className="grid size-7 place-items-center border border-foreground/20 transition-colors hover:border-foreground hover:bg-foreground hover:text-background"
  >
    {children}
  </button>
))

const Stat = memo(({ label, children }: { label: string; children: React.ReactNode }) => (
  <div className="bg-background px-3 py-2.5">
    <dt className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{label}</dt>
    <dd className="mt-1 truncate text-sm font-medium">{children}</dd>
  </div>
))

const PanelTitle = memo(({ left, right, live }: { left: string; right?: string; live?: boolean }) => (
  <div className="flex items-center justify-between border-b border-foreground/15 px-4 py-2.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
    <span className="flex items-center gap-2">
      {live ? (
        <span className="relative flex size-1.5">
          <span className="animate-pulse-ring absolute inset-0 bg-signal" />
          <span className="relative size-1.5 bg-signal" />
        </span>
      ) : null}
      {left}
    </span>
    {right ? <span>{right}</span> : null}
  </div>
))

const StatusDot = memo(({ phase }: { phase: string }) => {
  const done = phase === 'Complete'
  const paused = phase === 'Paused' || phase === 'Awaiting approval' || phase === 'Queued'
  return (
    <span
      aria-hidden="true"
      className={cn('size-1.5 shrink-0', done ? 'bg-signal' : paused ? 'border border-foreground' : 'bg-foreground animate-pulse')}
    />
  )
})

const FeatureIcon = memo(({ status }: { status: FeatureStatus }) => {
  const base = 'grid size-4 shrink-0 place-items-center'
  if (status === 'done')
    return (
      <span className={cn(base, 'bg-signal text-foreground')}>
        <Check className="size-3" aria-label="done" />
      </span>
    )
  if (status === 'running') return <Loader className="size-4 shrink-0 animate-spin text-signal-ink" aria-label="running" />
  if (status === 'failed')
    return (
      <span className={cn(base, 'bg-destructive text-background')}>
        <X className="size-3" aria-label="failed" />
      </span>
    )
  if (status === 'blocked')
    return (
      <span className={cn(base, 'border border-foreground')}>
        <Lock className="size-2.5" aria-label="blocked" />
      </span>
    )
  return <CircleDashed className="size-4 shrink-0 text-foreground/30" aria-label="queued" />
})

const CheckBadge = memo(({ status }: { status: CheckStatus }) => {
  const map: Record<CheckStatus, { label: string; cls: string }> = {
    idle: { label: 'idle', cls: 'border-foreground/15 text-foreground/40' },
    running: { label: 'run', cls: 'border-foreground text-foreground animate-pulse' },
    pass: { label: 'pass', cls: 'border-signal bg-signal text-foreground' },
    fail: { label: 'fail', cls: 'border-destructive bg-destructive text-background' },
  }
  const m = map[status]
  return (
    <span className={cn('min-w-11 border px-1.5 py-0.5 text-center font-mono text-[10px] uppercase tracking-wider', m.cls)}>
      {m.label}
    </span>
  )
})
