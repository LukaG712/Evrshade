'use client'

import { ChevronDown } from 'lucide-react'
import { INSTALLERS, RELEASES_BASE } from '@/lib/downloads'

export function DownloadDropdown() {
  return (
    <details className="group relative inline-block">
      <summary className="inline-flex h-11 cursor-pointer items-center gap-2 border border-foreground px-5 text-sm font-medium transition-colors hover:bg-foreground hover:text-background list-none focus-visible:outline-2 focus-visible:outline-offset-2">
        Download
        <ChevronDown className="size-4" aria-hidden="true" />
      </summary>
      <div className="absolute right-0 z-50 mt-2 w-[300px] border border-border bg-background/95 p-2 backdrop-blur-md">
        {INSTALLERS.map((inst) => (
          <a
            key={inst.file}
            href={`${RELEASES_BASE}/${inst.file}`}
            target="_blank"
            rel="noreferrer"
            className="block rounded px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            {inst.label}
          </a>
        ))}
      </div>
    </details>
  )
}
