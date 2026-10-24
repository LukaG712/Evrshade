'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { Check, Copy, Terminal, Dock, FolderGit, Monitor, Apple, ChevronRight, Cpu, HardDrive, Shield, Rocket } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PROFILES, SERVICES } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

type OS = 'macos' | 'windows' | 'linux' | 'unknown'

const detectOS = (): OS => {
  if (typeof window === 'undefined') return 'unknown'
  const ua = navigator.userAgent
  if (/Mac|iPhone|iPad|iPod/.test(ua)) return 'macos'
  if (/Win/.test(ua)) return 'windows'
  if (/Linux/.test(ua)) return 'linux'
  return 'unknown'
}

type InstallMethod = 'oneliner' | 'docker' | 'manual' | 'gui'

const METHODS: { id: InstallMethod; label: string; desc: string }[] = [
  { id: 'oneliner', label: 'One-liner', desc: 'Fastest path. Auto-detects your OS.' },
  { id: 'docker', label: 'Docker Compose', desc: 'Full control over every service.' },
  { id: 'manual', label: 'Manual clone', desc: 'Clone, configure, and start step by step.' },
  { id: 'gui', label: 'GUI Installer', desc: 'Visual step-by-step wizard.' },
]

const getOneLiner = (os: OS) => {
  switch (os) {
    case 'windows':
      return 'irm https://raw.githubusercontent.com/LukaG712/Evershade/master/install.ps1 | iex'
    default:
      return 'curl -fsSL https://raw.githubusercontent.com/LukaG712/Evershade/master/install.sh | sh'
  }
}

const getDockerCmd = (profile: string) => `docker compose --profile ${profile} up -d`

const MANUAL_STEPS = [
  { comment: '# clone the repository', cmd: 'git clone https://github.com/LukaG712/Evershade.git && cd Evershade' },
  { comment: '# install service repositories', cmd: './install.sh --profile minimal' },
  { comment: '# configure environment', cmd: 'cp .env.example .env' },
  { comment: '# start all services', cmd: './start.sh --profile minimal' },
]

const PREREQUISITES = [
  { icon: Dock, text: 'Docker Desktop or Docker Engine 24+', detail: 'Required for all install methods' },
  { icon: Terminal, text: 'Git', detail: 'For cloning the repository' },
  { icon: Shield, text: 'LLM API key or Ollama', detail: 'OpenAI, Anthropic, or local Ollama' },
  { icon: Cpu, text: '~512MB RAM minimum', detail: 'Minimal profile; ~2GB for full' },
  { icon: HardDrive, text: '~1GB disk space', detail: 'Docker images + service data' },
]

const POST_INSTALL_STEPS = [
  { title: 'Verify', body: 'Run evershade doctor to check everything is healthy.' },
  { title: 'Create an agent', body: 'Dashboard → Agents → Create. Pick a runner and model.' },
  { title: 'Run a mission', body: 'Open Chat, select your agent and type a prompt.' },
]

export function Install() {
  const [os, setOs] = useState<OS>('unknown')
  const [method, setMethod] = useState<InstallMethod>('oneliner')
  const [profile, setProfile] = useState('minimal')
  const [copied, setCopied] = useState(false)
  const [shownLines, setShownLines] = useState(0)
  const timerRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    setOs(detectOS())
  }, [])

  useEffect(() => {
    setShownLines(0)
  }, [method, profile])

  const lines = getTerminalLines(method, profile, os)

  useEffect(() => {
    if (shownLines >= lines.length) return
    const delay = shownLines === 0 ? 400 : 80
    timerRef.current = setTimeout(() => setShownLines((s) => s + 1), delay)
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [shownLines, lines.length])

  const currentCmd = getCurrentCommand(method, profile, os)

  const copy = useCallback(async () => {
    await navigator.clipboard.writeText(currentCmd)
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }, [currentCmd])

  return (
    <section id="install" aria-labelledby="install-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="install-title"
        label="Install"
        title={
          <>
            If it runs Docker,
            <br />
            <span className="text-muted-foreground">it runs Evershade.</span>
          </>
        }
        lead="Four install methods. Three profiles. One platform that runs anywhere Docker runs."
      />

      <div className="mt-12 grid gap-10 md:mt-16 md:grid-cols-12">
        {/* Main install area */}
        <div className="md:col-span-8">
          {/* Method tabs */}
          <div className="grid grid-cols-2 gap-px border border-foreground bg-foreground md:grid-cols-4">
            {METHODS.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => setMethod(m.id)}
                aria-pressed={m.id === method}
                className={cn(
                  'flex flex-col items-start gap-1 px-4 py-4 text-left transition-colors',
                  m.id === method
                    ? 'bg-foreground text-background'
                    : 'bg-background hover:bg-foreground/5',
                )}
              >
                <span className={cn(
                  'font-mono text-[10px] uppercase tracking-wider',
                  m.id === method ? 'text-signal' : 'text-muted-foreground',
                )}>
                  {m.label}
                </span>
                <span className="text-[11px] opacity-60">{m.desc}</span>
              </button>
            ))}
          </div>

          {/* Terminal output */}
          <div className="border-x border-b border-foreground">
            <div className="flex items-center justify-between border-b border-foreground px-4 py-2.5">
              <div className="flex items-center gap-2">
                {method === 'oneliner' && <Terminal className="size-3.5 text-muted-foreground" />}
                {method === 'docker' && <Dock className="size-3.5 text-muted-foreground" />}
                {method === 'manual' && <FolderGit className="size-3.5 text-muted-foreground" />}
                {method === 'gui' && <Monitor className="size-3.5 text-muted-foreground" />}
                <span className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                  {method === 'oneliner' ? (os === 'windows' ? 'powershell' : 'terminal') : method === 'docker' ? 'docker compose' : method === 'manual' ? 'bash' : 'installer'}
                </span>
              </div>
              <button
                type="button"
                onClick={copy}
                className="inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-wider transition-colors hover:text-signal-ink"
              >
                {copied ? <Check className="size-3.5 text-signal-ink" aria-hidden="true" /> : <Copy className="size-3.5" aria-hidden="true" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <pre className="min-h-[18rem] overflow-x-auto bg-foreground p-5 font-mono text-[12px] leading-relaxed text-background md:p-6 md:text-[13px]">
              <code aria-live="polite">
                {lines.slice(0, shownLines).map((line, i) => (
                  <span
                    key={`${method}-${profile}-${i}`}
                    className={cn(
                      'block',
                      line.tone === 'ok' && 'text-signal',
                      line.tone === 'dim' && 'opacity-50',
                      line.tone === 'cmd' && 'text-signal',
                      line.tone === 'warn' && 'underline decoration-dotted',
                    )}
                  >
                    {line.text}
                  </span>
                ))}
                {shownLines >= lines.length ? (
                  <span className="block">
                    <span className="text-signal">{'$ '}</span>
                    <span className="inline-block h-4 w-2 translate-y-0.5 animate-pulse bg-background" />
                  </span>
                ) : null}
              </code>
            </pre>
          </div>

          {/* Profile selector */}
          <div className="mt-8">
            <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Choose profile'}</p>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              {PROFILES.slice(0, 3).map((p) => (
                <button
                  key={p.name}
                  type="button"
                  onClick={() => setProfile(p.flag.replace('--profile ', ''))}
                  className={cn(
                    'flex flex-col items-start gap-2 border p-4 text-left transition-colors',
                    profile === p.flag.replace('--profile ', '')
                      ? 'border-foreground bg-foreground text-background'
                      : 'border-foreground hover:bg-foreground/5',
                  )}
                >
                  <div className="flex items-center gap-2">
                    <Rocket className={cn('size-4', profile === p.flag.replace('--profile ', '') ? 'text-signal' : 'text-muted-foreground')} />
                    <span className="font-semibold tracking-tight">{p.name}</span>
                  </div>
                  <span className={cn(
                    'text-sm',
                    profile === p.flag.replace('--profile ', '') ? 'opacity-70' : 'text-muted-foreground',
                  )}>
                    {p.detail}
                  </span>
                  <code className={cn(
                    'font-mono text-[10px]',
                    profile === p.flag.replace('--profile ', '') ? 'text-signal' : 'text-muted-foreground',
                  )}>
                    {p.flag}
                  </code>
                </button>
              ))}
            </div>
          </div>

          {/* Post-install steps */}
          <ol className="mt-8 grid gap-px border border-foreground bg-foreground sm:grid-cols-3">
            {POST_INSTALL_STEPS.map(([title, body], i) => (
              <li key={title} className="bg-background p-5">
                <div className="flex items-center gap-2">
                  <ChevronRight className="size-3 text-signal-ink" aria-hidden="true" />
                  <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{`Step ${i + 1}`}</p>
                </div>
                <p className="mt-3 font-semibold tracking-tight">{title}</p>
                <p className="mt-1 text-sm leading-snug text-muted-foreground">{body}</p>
              </li>
            ))}
          </ol>
        </div>

        {/* Sidebar */}
        <div className="md:col-span-4">
          {/* Detected OS */}
          <div className="border border-foreground p-5">
            <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Detected platform'}</p>
            <div className="mt-3 flex items-center gap-3">
              {os === 'macos' && <Apple className="size-5 text-muted-foreground" />}
              {os === 'windows' && <Monitor className="size-5 text-muted-foreground" />}
              {os === 'linux' && <Terminal className="size-5 text-muted-foreground" />}
              <div>
                <p className="font-semibold tracking-tight capitalize">{os === 'unknown' ? 'Unknown' : os}</p>
                <p className="text-xs text-muted-foreground">
                  {os === 'windows' ? 'PowerShell one-liner' : os === 'macos' ? 'curl + sh one-liner' : os === 'linux' ? 'curl + sh one-liner' : 'Select your method below'}
                </p>
              </div>
            </div>
          </div>

          {/* Prerequisites */}
          <div className="mt-6 border border-foreground p-5">
            <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Prerequisites'}</p>
            <ul className="mt-4 space-y-3">
              {PREREQUISITES.map((pr) => (
                <li key={pr.text} className="flex items-start gap-3">
                  <pr.icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
                  <div>
                    <p className="text-sm font-medium">{pr.text}</p>
                    <p className="text-xs text-muted-foreground">{pr.detail}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Services that will start */}
          <div className="mt-6 border border-foreground p-5">
            <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">
              {'Services · ' + getProfileServiceCount(profile)}
            </p>
            <ul className="mt-4 space-y-2">
              {getProfileServices(profile).map((svc) => (
                <li key={svc.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'size-1.5',
                      svc.tier === 'orchestrator' ? 'bg-signal' : svc.tier === 'core' ? 'bg-foreground' : 'border border-foreground',
                    )} />
                    <span className="text-sm">{svc.name}</span>
                  </div>
                  <span className="font-mono text-[10px] text-muted-foreground">
                    {svc.port === 'CLI' ? 'CLI' : `:${svc.port}`}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {/* Quick tip */}
          <div className="mt-6 rounded border border-dashed border-foreground/50 p-5">
            <p className="text-sm font-semibold tracking-tight">Already have Docker Compose?</p>
            <p className="mt-2 text-sm text-muted-foreground">
              Skip the installer and go straight to{' '}
              <a href="#try-it" className="text-signal-ink underline underline-offset-4">
                Docker Compose
              </a>{' '}
              with the one-liner.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

/* ── Helpers ── */

type Line = { text: string; tone?: 'ok' | 'dim' | 'cmd' | 'warn' }

function getTerminalLines(method: InstallMethod, profile: string, os: OS): Line[] {
  switch (method) {
    case 'oneliner':
      return [
        { text: os === 'windows' ? getOneLiner('windows') : getOneLiner('linux'), tone: 'cmd' },
        { text: '', tone: 'dim' },
        { text: `→ Detected platform: ${os === 'unknown' ? 'Linux/macOS' : os}`, tone: 'dim' },
        { text: `→ Profile: ${profile}`, tone: 'dim' },
        { text: '→ Cloning Evershade repository...', tone: 'ok' },
        { text: '→ Installing service repositories...', tone: 'ok' },
        { text: '→ Generating .env from template...', tone: 'ok' },
        { text: `→ Starting ${getProfileServiceCount(profile)} services...`, tone: 'ok' },
        { text: '', tone: 'dim' },
        ...getProfileServices(profile).map((svc) => ({
          text: `  ✓ ${svc.name.padEnd(14)} :${svc.port === 'CLI' ? '—' : svc.port}`,
          tone: 'ok' as const,
        })),
        { text: '', tone: 'dim' },
        { text: `✓ ${getProfileServiceCount(profile)}/${getProfileServiceCount(profile)} running · profile ${profile}`, tone: 'ok' },
        { text: '', tone: 'dim' },
        { text: '→ Dashboard: http://localhost:5173', tone: 'dim' },
        { text: '→ API:       http://localhost:8080', tone: 'dim' },
        { text: '', tone: 'dim' },
        { text: 'Run "evershade doctor" to verify your setup.', tone: 'warn' },
      ]
    case 'docker':
      return [
        { text: `$ ${getDockerCmd(profile)}`, tone: 'cmd' },
        { text: '', tone: 'dim' },
        { text: `→ Loading compose profile: ${profile}`, tone: 'dim' },
        { text: '→ Pulling images...', tone: 'dim' },
        ...getProfileServices(profile).map((svc) => ({
          text: `  evershade/${svc.id}  latest  Pulled`,
          tone: 'dim' as const,
        })),
        { text: '', tone: 'dim' },
        { text: '→ Creating containers...', tone: 'ok' },
        ...getProfileServices(profile).map((svc) => ({
          text: `  ✓ Created evershade-${svc.id}`,
          tone: 'ok' as const,
        })),
        { text: '', tone: 'dim' },
        { text: '→ Starting services...', tone: 'ok' },
        ...getProfileServices(profile).map((svc) => ({
          text: `  ✓ ${svc.name.padEnd(14)} :${svc.port === 'CLI' ? '—' : svc.port}  running`,
          tone: 'ok' as const,
        })),
        { text: '', tone: 'dim' },
        { text: `✓ ${getProfileServiceCount(profile)} services started`, tone: 'ok' },
        { text: '', tone: 'dim' },
        { text: '→ Tail logs: docker compose logs -f', tone: 'dim' },
        { text: '→ Stop:      docker compose down', tone: 'dim' },
      ]
    case 'manual':
      return MANUAL_STEPS.map((s, i, arr) =>
        i === arr.length - 1
          ? [{ text: s.comment, tone: 'dim' as const }, { text: s.cmd, tone: 'cmd' as const }, { text: '', tone: 'dim' as const },
            ...getProfileServices(profile).map((svc) => ({
              text: `  ✓ ${svc.name.padEnd(14)} :${svc.port === 'CLI' ? '—' : svc.port}  running`,
              tone: 'ok' as const,
            })),
            { text: '', tone: 'dim' as const },
            { text: `✓ ${getProfileServiceCount(profile)} services started`, tone: 'ok' as const }]
          : [{ text: s.comment, tone: 'dim' as const }, { text: s.cmd, tone: 'cmd' as const }, { text: '', tone: 'dim' as const }]
      ).flat()
    case 'gui':
      return [
        { text: '→ Launching Evershade Installer...', tone: 'cmd' },
        { text: '', tone: 'dim' },
        { text: '┌─────────────────────────────────────┐', tone: 'dim' },
        { text: '│     Evershade Installer             │', tone: 'dim' },
        { text: '├─────────────────────────────────────┤', tone: 'dim' },
        { text: '│                                     │', tone: 'dim' },
        { text: '│  [1] Welcome                        │', tone: 'ok' },
        { text: '│  [2] Prerequisites check            │', tone: 'ok' },
        { text: '│  [3] Profile selection              │', tone: 'dim' },
        { text: '│  [4] Configuration                  │', tone: 'dim' },
        { text: '│  [5] Install & start                │', tone: 'dim' },
        { text: '│  [6] Verify                         │', tone: 'dim' },
        { text: '│                                     │', tone: 'dim' },
        { text: '│  Profile: ○ Minimal  ● Standard    │', tone: 'dim' },
        { text: '│                                     │', tone: 'dim' },
        { text: '│  [Next]        [Cancel]             │', tone: 'dim' },
        { text: '└─────────────────────────────────────┘', tone: 'dim' },
        { text: '', tone: 'dim' },
        { text: '→ Download the GUI installer from GitHub Releases.', tone: 'warn' },
        { text: `→ ${os === 'windows' ? 'evershade-windows-amd64.exe' : 'evershade-installer.AppImage'}`, tone: 'dim' },
      ]
  }
}

function getCurrentCommand(method: InstallMethod, profile: string, os: OS): string {
  switch (method) {
    case 'oneliner':
      return getOneLiner(os)
    case 'docker':
      return getDockerCmd(profile)
    case 'manual':
      return MANUAL_STEPS.map((s) => s.cmd).join('\n')
    case 'gui':
      return 'https://github.com/LukaG712/Evershade/releases'
  }
}

function getProfileServices(profile: string) {
  const coreIds = ['greenie', 'slinker', 'trapper', 'gobber']
  const allIds = ['greenie', 'slinker', 'trapper', 'gobber', 'shrewd', 'sneaker', 'hider', 'poltergeist']
  const fullIds = [...allIds, 'slammer', 'speedy']

  let ids: string[]
  switch (profile) {
    case 'standard':
      ids = allIds
      break
    case 'full':
      ids = fullIds
      break
    default:
      ids = coreIds
  }

  return SERVICES.filter((s) => ids.includes(s.id))
}

function getProfileServiceCount(profile: string): number {
  return getProfileServices(profile).length
}
