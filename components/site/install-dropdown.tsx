'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { ChevronDown, Copy, Check, Apple, Monitor, Terminal } from 'lucide-react'

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
  { os: 'macos' as OS, label: 'macOS', subtitle: 'Apple Silicon (M1/M2/M3)', file: 'evershade-darwin-arm64.tar.gz', icon: Apple },
  { os: 'macos' as OS, label: 'macOS', subtitle: 'Intel (x86_64)', file: 'evershade-darwin-amd64.tar.gz', icon: Apple },
  { os: 'linux' as OS, label: 'Linux', subtitle: 'x86_64 (Debian/Ubuntu)', file: 'evershade-linux-amd64.tar.gz', icon: Terminal },
  { os: 'linux' as OS, label: 'Linux', subtitle: 'ARM64', file: 'evershade-linux-arm64.tar.gz', icon: Terminal },
  { os: 'windows' as OS, label: 'Windows', subtitle: 'x86_64 (Installer)', file: 'evershade-windows-amd64.exe', icon: Monitor },
] as const

export function InstallDropdown() {
  const [open, setOpen] = useState(false)
  const [os, setOs] = useState<OS>('unknown')
  const [copied, setCopied] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setOs(detectOS())
  }, [])

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  const copy = useCallback(async () => {
    await navigator.clipboard.writeText(getCurlCommand(os))
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }, [os])

  const curlCmd = getCurlCommand(os)

  return (
    <div className="flex flex-col gap-2" ref={dropdownRef}>
      {/* One-liner box */}
      <div className="border border-foreground">
        <div className="flex items-center justify-between border-b border-foreground px-3 py-1.5">
          <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
            {os === 'windows' ? 'powershell' : 'terminal'}
          </span>
          <button
            type="button"
            onClick={copy}
            className="inline-flex items-center gap-1 font-mono text-[10px] uppercase tracking-wider transition-colors hover:text-signal-ink"
          >
            {copied ? <Check className="size-3 text-signal-ink" aria-hidden="true" /> : <Copy className="size-3" aria-hidden="true" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
        <div className="p-3">
          <code className="font-mono text-[11px] leading-relaxed">{curlCmd}</code>
        </div>
      </div>

      {/* Dropdown button */}
      <div className="relative">
        <button
          type="button"
          onClick={() => setOpen(!open)}
          className="inline-flex h-11 items-center gap-2 bg-foreground px-5 text-sm font-medium text-background transition-colors hover:bg-signal-ink"
        >
          Install Evershade
          <ChevronDown className={`size-4 transition-transform ${open ? 'rotate-180' : ''}`} aria-hidden="true" />
        </button>

        {open && (
          <div className="absolute right-0 top-full z-50 mt-2 w-[320px] border border-foreground bg-background p-2 shadow-lg">
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
                </a>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
