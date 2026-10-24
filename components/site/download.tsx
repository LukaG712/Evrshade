'use client'

import { useState, useEffect, useCallback } from 'react'
import { ChevronDown, Download, Copy, Check, Apple, Monitor, Terminal } from 'lucide-react'
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

const getCurlCommand = (os: OS) => {
  switch (os) {
    case 'macos':
      return 'curl -fsSL https://raw.githubusercontent.com/LukaG712/Evershade/master/install.sh | sh'
    case 'windows':
      return 'irm https://raw.githubusercontent.com/LukaG712/Evershade/master/install.ps1 | iex'
    case 'linux':
      return 'curl -fsSL https://raw.githubusercontent.com/LukaG712/Evershade/master/install.sh | sh'
    default:
      return 'curl -fsSL https://raw.githubusercontent.com/LukaG712/Evershade/master/install.sh | sh'
  }
}

const installers = [
  {
    os: 'macos' as OS,
    label: 'macOS',
    subtitle: 'Apple Silicon (M1/M2/M3)',
    file: 'evershade-darwin-arm64.tar.gz',
    icon: Apple,
  },
  {
    os: 'macos' as OS,
    label: 'macOS',
    subtitle: 'Intel (x86_64)',
    file: 'evershade-darwin-amd64.tar.gz',
    icon: Apple,
  },
  {
    os: 'linux' as OS,
    label: 'Linux',
    subtitle: 'x86_64 (Debian/Ubuntu)',
    file: 'evershade-linux-amd64.tar.gz',
    icon: Terminal,
  },
  {
    os: 'linux' as OS,
    label: 'Linux',
    subtitle: 'ARM64',
    file: 'evershade-linux-arm64.tar.gz',
    icon: Terminal,
  },
  {
    os: 'windows' as OS,
    label: 'Windows',
    subtitle: 'x86_64 (Installer)',
    file: 'evershade-windows-amd64.exe',
    icon: Monitor,
  },
] as const

export function Download() {
  const [open, setOpen] = useState(false)
  const [os, setOs] = useState<OS>('unknown')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    setOs(detectOS())
  }, [])

  const copy = useCallback(async () => {
    await navigator.clipboard.writeText(getCurlCommand(os))
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }, [os])

  const curlCmd = getCurlCommand(os)
  const CmdIcon = os === 'windows' ? Monitor : Terminal

  return (
    <section id="download" aria-labelledby="download-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="download-title"
        label="Download"
        title={
          <>
            Get
            <span className="text-signal"> started.</span>
          </>
        }
        lead="Download a pre-built binary for your platform, or use the one-liner to install automatically."
      />

      <div className="mt-12 grid gap-10 md:mt-16 md:grid-cols-12">
        {/* Curl one-liner */}
        <div className="md:col-span-7">
          <div className="border border-foreground">
            <div className="flex items-center justify-between border-b border-foreground px-4 py-2.5">
              <span className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                {os === 'windows' ? 'powershell' : 'terminal'}
              </span>
              <button
                type="button"
                onClick={copy}
                className="inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-wider transition-colors hover:text-signal-ink"
              >
                {copied ? <Check className="size-3.5 text-signal-ink" aria-hidden="true" /> : <Copy className="size-3.5" aria-hidden="true" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <div className="p-5 md:p-6">
              <div className="flex items-center gap-2">
                <CmdIcon className="size-4 text-muted-foreground" aria-hidden="true" />
                <code className="font-mono text-sm">{curlCmd}</code>
              </div>
              <p className="mt-3 text-sm text-muted-foreground">
                {os === 'windows'
                  ? 'PowerShell one-liner for Windows. Downloads and runs the install script.'
                  : 'Downloads and runs the install script. Requires curl and a POSIX shell.'}
              </p>
            </div>
          </div>

          {/* Dropdown button */}
          <div className="mt-6 relative">
            <button
              type="button"
              onClick={() => setOpen(!open)}
              className="inline-flex h-12 items-center gap-2 bg-foreground px-6 text-sm font-medium text-background transition-colors hover:bg-signal-ink"
            >
              <Download className="size-4" aria-hidden="true" />
              Download all installers
              <ChevronDown className={`size-4 transition-transform ${open ? 'rotate-180' : ''}`} aria-hidden="true" />
            </button>

            {open && (
              <div className="absolute left-0 top-full z-50 mt-2 w-full min-w-[320px] border border-foreground bg-background p-2 shadow-lg">
                {installers.map((item) => {
                  const Icon = item.icon
                  return (
                    <a
                      key={item.file}
                      href={`https://github.com/LukaG712/Evershade/releases/latest/download/${item.file}`}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-3 rounded p-3 transition-colors hover:bg-foreground/5"
                      onClick={() => setOpen(false)}
                    >
                      <Icon className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
                      <div className="min-w-0">
                        <p className="text-sm font-semibold tracking-tight">{item.label}</p>
                        <p className="font-mono text-[10px] text-muted-foreground">{item.subtitle}</p>
                      </div>
                      <span className="ml-auto font-mono text-[10px] text-muted-foreground">{item.file}</span>
                    </a>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Quick info */}
        <div className="md:col-span-4 md:col-start-9">
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

          <div className="mt-6 rounded border border-dashed border-foreground/50 p-5">
            <p className="text-sm font-semibold tracking-tight">Prefer Docker only?</p>
            <p className="mt-2 text-sm text-muted-foreground">
              Skip the binary and go straight to{' '}
              <a href="#docker" className="text-signal-ink underline underline-offset-4">
                Docker Compose
              </a>{' '}
              with the one-liner on the Try it section.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
