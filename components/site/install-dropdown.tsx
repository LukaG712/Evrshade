'use client'

import { useState, useEffect, useCallback } from 'react'
import { Copy, Check } from 'lucide-react'

type OS = 'macos' | 'windows' | 'linux' | 'unknown'

const detectOS = (): OS => {
  if (typeof window === 'undefined') return 'unknown'
  const ua = navigator.userAgent
  if (/Mac|iPhone|iPad|iPod/.test(ua)) return 'macos'
  if (/Win/.test(ua)) return 'windows'
  if (/Linux/.test(ua)) return 'linux'
  return 'unknown'
}

const getInstallCommand = (os: OS) => {
  switch (os) {
    case 'macos':
    case 'linux':
      return 'git clone https://github.com/LukaG712/Evershade.git && cd Evershade && docker compose --profile standard up -d'
    case 'windows':
      return 'git clone https://github.com/LukaG712/Evershade.git; cd Evershade; docker compose --profile standard up -d'
    default:
      return 'git clone https://github.com/LukaG712/Evershade.git && cd Evershade && docker compose --profile standard up -d'
  }
}

export function InstallDropdown() {
  const [os, setOs] = useState<OS>('unknown')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    setOs(detectOS())
  }, [])

  const copy = useCallback(async () => {
    await navigator.clipboard.writeText(getInstallCommand(os))
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }, [os])

  const installCmd = getInstallCommand(os)

  return (
    <div className="group relative">
      <div className="pointer-events-none absolute -inset-1.5 rounded-sm bg-gradient-to-r from-signal/10 to-signal/5 opacity-0 transition-opacity group-hover:opacity-100" />
      <div className="relative overflow-hidden rounded-sm border border-border bg-muted/30">
        <div className="flex items-center justify-between border-b border-border px-3 py-2">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <span className="size-2 rounded-full bg-foreground/15" />
              <span className="size-2 rounded-full bg-foreground/15" />
              <span className="size-2 rounded-full bg-foreground/15" />
            </div>
            <span className="ml-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
              {os === 'windows' ? 'powershell' : 'terminal'}
            </span>
          </div>
          <button
            type="button"
            onClick={copy}
            className="inline-flex items-center gap-1.5 rounded-sm px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground transition-colors hover:text-signal-ink"
          >
            {copied ? <Check className="size-3 text-signal-ink" aria-hidden="true" /> : <Copy className="size-3" aria-hidden="true" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
        <div className="px-3 py-2.5">
          <code className="font-mono text-[11px] leading-relaxed text-foreground/90">
            <span className="select-none text-signal-ink">$ </span>
            {installCmd}
          </code>
        </div>
      </div>
    </div>
  )
}
