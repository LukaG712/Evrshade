'use client'

import { Check, Link } from 'lucide-react'
import { useState, useCallback } from 'react'

export function SectionHeading({
  label,
  title,
  lead,
  id,
}: {
  label: string
  title: React.ReactNode
  lead?: React.ReactNode
  id: string
}) {
  const [copied, setCopied] = useState(false)

  const copyLink = useCallback(() => {
    navigator.clipboard.writeText(`#${id}`)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }, [id])

  return (
    <div className="grid gap-6 border-t border-foreground pt-6 md:grid-cols-12 md:gap-8">
      <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground md:col-span-3">{label}</p>
      <div className="md:col-span-9">
        <div className="flex items-center gap-2">
          <h3 id={id} className="text-balance text-4xl font-semibold leading-[0.9] tracking-[-0.05em] md:text-6xl lg:text-7xl">
            {title}
          </h3>
          <button
            type="button"
            onClick={copyLink}
            className="shrink-0 opacity-0 transition-opacity group-hover:opacity-100 hover:text-signal-ink focus:opacity-100"
            aria-label={`Copy link to ${label}`}
          >
            {copied ? <Check className="size-4 text-signal-ink" /> : <Link className="size-4" />}
          </button>
        </div>
        {lead ? <p className="mt-6 max-w-2xl text-pretty text-lg leading-snug text-muted-foreground md:text-xl">{lead}</p> : null}
      </div>
    </div>
  )
}
