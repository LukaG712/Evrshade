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
  const history = releases.slice(1, 6)

  return (
    <section id="changelog" className="px-4 pt-24 md:px-[max(24px,3vw)] md:pt-40">
      <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Latest release'}</p>

      {loaded && latest && (
        <div className="mt-4 border border-foreground p-4">
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
                {changes.slice(0, 4).map((change) => (
                  <li key={change} className="flex items-start gap-2 text-sm leading-snug">
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-signal-ink" />
                    {change}
                  </li>
                ))}
              </ul>
            )
          })()}
        </div>
      )}

      <p className="mt-8 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Release history'}</p>
      <div className="mt-4 space-y-0">
        {loaded && history.map((release) => {
          const d = formatDate(release.publishedAt)
          const note = (() => {
            const lines = release.body.split('\n')
            for (const line of lines) {
              const trimmed = line.trim()
              if (/^[-*]\s/.test(trimmed) && trimmed.length < 80) {
                return trimmed.replace(/^[-*]\s+/, '')
              }
            }
            return release.name
          })()
          return (
            <div key={release.tag} className="border-b border-border py-3">
              <div className="flex items-baseline justify-between gap-4">
                <span className="font-mono text-sm font-semibold">{release.tag}</span>
                <span className="font-mono text-[11px] text-muted-foreground">{d.label}</span>
              </div>
              <p className="mt-0.5 text-xs text-muted-foreground">{note}</p>
            </div>
          )
        })}
      </div>
      <a
        href={`${REPO_URL}/releases`}
        target="_blank"
        rel="noreferrer"
        className="group mt-4 inline-flex items-center gap-1 text-sm font-medium underline underline-offset-2 hover:text-signal-ink"
      >
        Full changelog
        <ArrowUpRight className="size-3.5 opacity-40 transition-opacity group-hover:opacity-100" aria-hidden="true" />
      </a>
    </section>
  )
}
