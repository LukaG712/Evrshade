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
    <div className="border border-foreground">
      <div className="flex items-center justify-between border-b border-foreground px-2 py-2 sm:px-3 sm:py-1.5">
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
          {os === 'windows' ? 'powershell' : 'terminal'}
        </span>
        <button
          type="button"
          onClick={copy}
          className="inline-flex items-center gap-1 rounded-md px-2 py-1.5 font-mono text-[10px] uppercase tracking-wider transition-colors hover:text-signal-ink"
        >
          {copied ? <Check className="size-3 text-signal-ink" aria-hidden="true" /> : <Copy className="size-3" aria-hidden="true" />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <div className="p-2 sm:p-3">
        <code className="break-all font-mono text-[11px] leading-relaxed">{installCmd}</code>
      </div>
    </div>
  )
}
