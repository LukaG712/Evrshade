'use client'

import { useEffect, useState } from 'react'
import { ArrowUpRight } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'

interface Release {
  tag: string
  name: string
  publishedAt: string
  body: string
  url: string
}

function parseReleaseBody(body: string): string[] {
  if (!body) return []
  // Extract list items (lines starting with - or *) and heading-like lines
  const lines = body.split('\n')
  const items: string[] = []
  for (const line of lines) {
    const trimmed = line.trim()
    // Match bullet points
    if (/^[-*]\s/.test(trimmed)) {
      items.push(trimmed.replace(/^[-*]\s+/, ''))
    }
    // Match short lines that look like changelog entries (not headers, not empty, not too long)
    else if (trimmed.length > 0 && trimmed.length < 120 && !/^#+\s/.test(trimmed) && !/\|/.test(trimmed)) {
      items.push(trimmed)
    }
  }
  // Return up to 8 items
  return items.slice(0, 8)
}

function formatDate(dateStr: string): { label: string; dateTime: string } {
  const date = new Date(dateStr)
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return {
    label: `${months[date.getMonth()]} ${date.getFullYear()}`,
    dateTime: date.toISOString().split('T')[0],
  }
}

export function ChangelogTicker() {
  const [releases, setReleases] = useState<Release[]>([])
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    fetch('/api/releases-json')
      .then((res) => res.json())
      .then((data) => {
        setReleases(data)
        setLoaded(true)
      })
      .catch(() => setLoaded(true))
  }, [])

  const latest = releases[0]
  const history = releases.slice(1, 4)

  return (
    <section id="changelog" className="px-4 pt-24 md:px-[max(24px,3vw)] md:pt-40">
      <div className="flex items-baseline justify-between">
        <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Releases'}</p>
        <a
          href={`${REPO_URL}/releases`}
          target="_blank"
          rel="noreferrer"
          className="group inline-flex items-center gap-1 text-xs font-medium text-muted-foreground underline underline-offset-2 hover:text-foreground"
        >
          View all
          <ArrowUpRight className="size-3 opacity-40 transition-opacity group-hover:opacity-100" aria-hidden="true" />
        </a>
      </div>

      {loaded && latest && (
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {/* Latest release - prominent */}
          <div className="border border-foreground p-4 md:col-span-2">
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center rounded-full border border-signal bg-signal/10 px-2.5 py-0.5 font-mono text-[11px] font-bold uppercase tracking-wider text-signal-ink">
                {latest.tag}
              </span>
              {(() => {
                const d = formatDate(latest.publishedAt)
                return <time className="font-mono text-[11px] text-muted-foreground" dateTime={d.dateTime}>{d.label}</time>
              })()}
            </div>
            {(() => {
              const changes = parseReleaseBody(latest.body)
              if (changes.length === 0) return null
              return (
                <ul className="mt-3 space-y-1">
                  {changes.slice(0, 3).map((change) => (
                    <li key={change} className="flex items-start gap-2 text-sm leading-snug">
                      <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-signal-ink" />
                      {change}
                    </li>
                  ))}
                </ul>
              )
            })()}
          </div>

          {/* Release history - compact list */}
          {history.map((release) => {
            const d = formatDate(release.publishedAt)
            return (
              <div key={release.tag} className="flex items-center justify-between border border-border p-3">
                <span className="font-mono text-sm font-semibold">{release.tag}</span>
                <span className="font-mono text-[11px] text-muted-foreground">{d.label}</span>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
