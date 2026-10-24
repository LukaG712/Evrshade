'use client'

import { useState } from 'react'
import { Check, Link2 } from 'lucide-react'

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

  const handleCopy = async (e: React.MouseEvent) => {
    e.preventDefault()
    const url = `${window.location.origin}${window.location.pathname}#${id}`
    try {
      await navigator.clipboard.writeText(url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      const input = document.createElement('input')
      input.value = url
      document.body.appendChild(input)
      input.select()
      document.execCommand('copy')
      document.body.removeChild(input)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="grid gap-6 border-t border-foreground pt-6 md:grid-cols-12 md:gap-8">
      <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground md:col-span-3">{label}</p>
      <div className="md:col-span-9">
        <div className="relative inline-flex items-center gap-2">
          <h3
            id={id}
            className="cursor-pointer text-balance text-2xl font-semibold leading-[0.9] tracking-[-0.05em] md:text-5xl lg:text-7xl"
            onClick={handleCopy}
            title="Click to copy link"
          >
            {title}
          </h3>
          <button
            onClick={handleCopy}
            className="shrink-0 text-muted-foreground/40 transition-colors hover:text-signal-ink focus-visible:outline-2 focus-visible:outline-offset-2"
            aria-label="Copy link to this section"
            type="button"
          >
            {copied ? (
              <Check className="size-4 text-signal" aria-hidden="true" />
            ) : (
              <Link2 className="size-4" aria-hidden="true" />
            )}
          </button>
        </div>
        {lead ? <p className="mt-4 max-w-2xl text-pretty text-base leading-snug text-muted-foreground md:mt-6 md:text-xl">{lead}</p> : null}
      </div>
    </div>
  )
}
