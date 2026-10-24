'use client'

import { useState } from 'react'
import { ChevronDown, Download as DownloadIcon } from 'lucide-react'
import { INSTALLERS, RELEASES_BASE_URL } from '@/lib/downloads'

export function DownloadDropdown() {
  const [open, setOpen] = useState(false)

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="inline-flex h-11 items-center gap-2 border border-foreground px-5 text-sm font-medium transition-colors hover:bg-foreground hover:text-background"
      >
        <DownloadIcon className="size-4" aria-hidden="true" />
        Download
        <ChevronDown className={`size-4 transition-transform ${open ? 'rotate-180' : ''}`} aria-hidden="true" />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} aria-hidden="true" />
          <div className="absolute right-0 top-full z-50 mt-2 w-[300px] border border-foreground bg-background p-2 shadow-lg">
            {INSTALLERS.map((item) => {
              const Icon = item.icon
              return (
                <a
                  key={item.file}
                  href={`${RELEASES_BASE_URL}/${item.file}`}
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
        </>
      )}
    </div>
  )
}
