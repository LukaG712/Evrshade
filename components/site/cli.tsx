'use client'

import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'
import { SectionHeading } from './section-heading'

type Line = { text: string; tone?: 'ok' | 'dim' | 'warn' }

const CMDS: { cmd: string; what: string; out: Line[] }[] = [
  {
    cmd: 'evershade status',
    what: 'Health of every service at a glance.',
    out: [
      { text: 'SERVICE       PORT   STATUS    VERSION', tone: 'dim' },
      { text: 'greenie       8080   healthy   1.8.0', tone: 'ok' },
      { text: 'slinker       8000   healthy   1.2.0', tone: 'ok' },
      { text: 'trapper       3000   healthy   1.1.0', tone: 'ok' },
      { text: 'gobber        8085   healthy   1.1.0', tone: 'ok' },
      { text: 'shrewd        8089   healthy', tone: 'ok' },
      { text: 'sneaker       8086   healthy   1.2.0', tone: 'ok' },
      { text: 'hider         8087   healthy   1.1.0', tone: 'ok' },
      { text: 'poltergeist   8088   healthy', tone: 'ok' },
      { text: '' },
      { text: 'ecosystem v1.14.0 · 8/8 healthy · profile standard' },
    ],
  },
  {
    cmd: 'evershade doctor',
    what: 'Diagnose Docker, ports, config and keys.',
    out: [
      { text: '✓ docker engine reachable', tone: 'ok' },
      { text: '✓ compose profile "standard" resolved', tone: 'ok' },
      { text: '✓ ports 8080 8000 3000 8085-8089 free or owned', tone: 'ok' },
      { text: '✓ .env present · API keys set', tone: 'ok' },
      { text: '✓ ENCRYPTION_KEY set for Hider (AES-256-GCM)', tone: 'ok' },
      { text: '! no external LLM key · using Ollama only', tone: 'warn' },
      { text: '' },
      { text: '5 passed · 1 warning' },
    ],
  },
  {
    cmd: 'evershade agents list',
    what: 'Agents, runners and their models.',
    out: [
      { text: 'NAME         RUNNER   MODEL              ISOLATION', tone: 'dim' },
      { text: 'researcher   junie    routed by shrewd   container' },
      { text: 'reviewer     junie    routed by shrewd   container' },
      { text: 'builder      junie    ollama (local)     workstation' },
    ],
  },
  {
    cmd: 'evershade backup create',
    what: 'Snapshot every service’s SQLite data.',
    out: [
      { text: '→ greenie   missions.db  checkpoints.db', tone: 'dim' },
      { text: '→ gobber    knowledge.db', tone: 'dim' },
      { text: '→ hider     secrets.db (remains encrypted)', tone: 'dim' },
      { text: '→ poltergeist notifications.db', tone: 'dim' },
      { text: '✓ backup written · verify with --verify', tone: 'ok' },
    ],
  },
  {
    cmd: 'evershade config validate',
    what: 'Catch configuration errors before start.',
    out: [
      { text: '✓ .env schema valid', tone: 'ok' },
      { text: '✓ service URLs resolve on evershade network', tone: 'ok' },
      { text: '✓ no hardcoded localhost references', tone: 'ok' },
    ],
  },
]

export function Cli() {
  const [active, setActive] = useState(0)
  const [shown, setShown] = useState(0)
  const cur = CMDS[active]

  useEffect(() => {
    if (shown >= cur.out.length) return
    const id = window.setTimeout(() => setShown((s) => s + 1), shown === 0 ? 350 : 70)
    return () => window.clearTimeout(id)
  }, [shown, cur.out.length])

  const run = (i: number) => {
    setActive(i)
    setShown(0)
  }

  return (
    <section id="cli" aria-labelledby="cli-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="cli-title"
        label="Speedy CLI"
        title={
          <>
            Operate it
            <br />
            <span className="text-muted-foreground">from one command.</span>
          </>
        }
        lead="Speedy is the evershade command. It installs, starts, stops, diagnoses, tails logs, backs up and restores the whole ecosystem."
      />

      <div className="mt-12 grid gap-px border border-foreground bg-foreground md:mt-24 lg:grid-cols-12">
        <ul className="bg-background lg:col-span-4" aria-label="Commands">
          {CMDS.map((c, i) => (
            <li key={c.cmd} className="border-b border-border last:border-b-0">
              <button
                type="button"
                onClick={() => run(i)}
                aria-pressed={i === active}
                className={cn(
                  'flex w-full flex-col items-start gap-1 px-5 py-4 text-left transition-colors',
                  i === active ? 'bg-foreground text-background' : 'hover:bg-foreground/5',
                )}
              >
                <code className="font-mono text-sm">
                  <span className={i === active ? 'text-signal' : 'text-signal-ink'}>{'$ '}</span>
                  {c.cmd}
                </code>
                <span className="text-sm opacity-60">{c.what}</span>
              </button>
            </li>
          ))}
        </ul>

        <div className="flex min-h-[22rem] flex-col bg-foreground text-background lg:col-span-8">
          <div className="flex items-center justify-between border-b border-background/15 px-5 py-2.5 font-mono text-[10px] uppercase tracking-wider opacity-60">
            <span>{'~/evershade - zsh'}</span>
            <span>{'Example output'}</span>
          </div>
          <pre className="flex-1 overflow-x-auto p-5 font-mono text-[12px] leading-relaxed md:p-6 md:text-[13px]" aria-live="polite">
            <code>
              <span className="text-signal">{'$ '}</span>
              {cur.cmd}
              {'\n'}
              {cur.out.slice(0, shown).map((l, i) => (
                <span
                  key={`${active}-${i}`}
                  className={cn('block', l.tone === 'ok' && 'text-signal', l.tone === 'dim' && 'opacity-50', l.tone === 'warn' && 'text-background underline decoration-dotted')}
                >
                  {l.text || ' '}
                </span>
              ))}
              {shown >= cur.out.length ? (
                <span className="block">
                  <span className="text-signal">{'$ '}</span>
                  <span className="inline-block h-4 w-2 translate-y-0.5 animate-pulse bg-background" />
                </span>
              ) : null}
            </code>
          </pre>
        </div>
      </div>
    </section>
  )
}
