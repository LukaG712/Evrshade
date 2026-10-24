'use client'

import { useEffect, useState } from 'react'
import { Tag } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

interface Release {
  tag_name: string
  name: string
  published_at: string
  prerelease: boolean
  body: string
}

export function Changelog() {
  const [releases, setReleases] = useState<Release[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('https://api.github.com/repos/LukaG712/Evershade/releases?per_page=20')
      .then((res) => {
        if (!res.ok) return []
        return res.json()
      })
      .then((data: Release[]) => {
        if (Array.isArray(data)) setReleases(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  return (
    <section id="changelog" aria-labelledby="changelog-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="changelog-title"
        label="Changelog"
        title={
          <>
            Every release,
            <br />
            <span className="text-muted-foreground">tracked.</span>
          </>
        }
        lead="Auto-generated from GitHub releases. No placeholder text, no made-up dates."
      />

      <div className="mt-16">
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse border border-border p-5">
                <div className="h-4 w-24 rounded bg-muted" />
                <div className="mt-3 h-3 w-40 rounded bg-muted" />
              </div>
            ))}
          </div>
        ) : releases.length === 0 ? (
          <div className="border border-dashed border-border p-8 text-center">
            <Tag className="mx-auto size-5 text-muted-foreground" aria-hidden="true" />
            <p className="mt-3 text-sm text-muted-foreground">
              No releases yet. When the first GitHub release is published, it'll appear here automatically.
            </p>
            <a
              href={`${REPO_URL}/releases`}
              target="_blank"
              rel="noreferrer"
              className="mt-4 inline-flex items-center gap-1 text-sm font-medium underline underline-offset-2 hover:text-signal-ink"
            >
              View releases on GitHub
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {releases.map((release) => (
              <a
                key={release.tag_name}
                href={`${REPO_URL}/releases/tag/${release.tag_name}`}
                target="_blank"
                rel="noreferrer"
                className="block border border-foreground p-5 transition-colors hover:bg-muted/50"
              >
                <div className="flex items-center gap-3">
                  <span className="inline-flex items-center rounded-full border border-signal bg-signal/10 px-2.5 py-0.5 font-mono text-[11px] font-bold uppercase tracking-wider text-signal-ink">
                    {release.tag_name}
                  </span>
                  {release.prerelease && (
                    <span className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                      Pre-release
                    </span>
                  )}
                  <time className="font-mono text-[11px] text-muted-foreground" dateTime={release.published_at}>
                    {new Date(release.published_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </time>
                </div>
                {release.name && (
                  <p className="mt-2 font-semibold tracking-tight">{release.name}</p>
                )}
                {release.body && (
                  <p className="mt-2 line-clamp-2 text-sm leading-snug text-muted-foreground">
                    {release.body.split('\n')[0]}
                  </p>
                )}
              </a>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
