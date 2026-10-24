'use client'

import { useEffect, useState } from 'react'
import { ArrowUpRight, Tag, Calendar, GitCommit } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

type Release = {
  tag_name: string
  name: string
  published_at: string
  html_url: string
  body: string
  prerelease: boolean
}

export function Changelog() {
  const [releases, setReleases] = useState<Release[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('https://api.github.com/repos/LukaG712/Evershade/releases?per_page=10')
      .then((res) => {
        if (!res.ok) throw new Error('Failed')
        return res.json()
      })
      .then((data: Release[]) => {
        setReleases(data)
      })
      .catch(() => {
        // Silently fail — show fallback state
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  return (
    <section id="changelog" aria-labelledby="changelog-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="changelog-title"
        label="Changelog"
        title={<>What shipped<span className="text-signal">.</span></>}
        lead="Real releases from the GitHub repository, not a placeholder. See what changed in every version of Evershade."
      />

      {loading ? (
        <div className="mt-12 space-y-4 md:mt-16">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse border border-border p-5">
              <div className="h-4 w-24 rounded bg-muted" />
              <div className="mt-3 h-3 w-16 rounded bg-muted" />
              <div className="mt-3 space-y-2">
                <div className="h-3 w-full rounded bg-muted" />
                <div className="h-3 w-3/4 rounded bg-muted" />
              </div>
            </div>
          ))}
        </div>
      ) : releases.length === 0 ? (
        <div className="mt-12 border border-dashed border-border p-8 text-center md:mt-16">
          <GitCommit className="mx-auto size-6 text-muted-foreground" aria-hidden="true" />
          <p className="mt-3 font-medium">No releases yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Evershade is under active development. Releases will appear here once published.
          </p>
          <a
            href={`${REPO_URL}/releases`}
            target="_blank"
            rel="noreferrer"
            className="mt-4 inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-wider text-signal-ink transition-colors hover:underline"
          >
            Check GitHub releases
            <ArrowUpRight className="size-3" aria-hidden="true" />
          </a>
        </div>
      ) : (
        <div className="mt-12 stagger space-y-4 md:mt-16">
          {releases.map((release) => (
            <a
              key={release.tag_name}
              href={release.html_url}
              target="_blank"
              rel="noreferrer"
              className="group block border border-border p-5 transition-colors hover:border-signal"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Tag className="size-4 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
                  <span className="font-semibold tracking-tight">{release.name || release.tag_name}</span>
                  {release.prerelease && (
                    <span className="rounded-full border border-amber-500/40 bg-amber-500/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-amber-600">
                      prerelease
                    </span>
                  )}
                </div>
                <ArrowUpRight className="size-4 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
              </div>
              <div className="mt-2 flex items-center gap-4">
                <span className="inline-flex items-center gap-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  {release.tag_name}
                </span>
                <span className="inline-flex items-center gap-1 font-mono text-[10px] text-muted-foreground">
                  <Calendar className="size-3" aria-hidden="true" />
                  {new Date(release.published_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })}
                </span>
              </div>
              <p className="mt-3 whitespace-pre-line text-sm leading-snug text-muted-foreground">
                {release.body}
              </p>
            </a>
          ))}
        </div>
      )}
    </section>
  )
}
