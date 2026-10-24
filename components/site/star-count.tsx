'use client'

import { useEffect, useState } from 'react'
import { Star } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'

export function StarCount() {
  const [stars, setStars] = useState<number | null>(null)

  useEffect(() => {
    fetch('https://api.github.com/repos/LukaG712/Evershade')
      .then((res) => {
        if (!res.ok) return
        return res.json()
      })
      .then((data: { stargazers_count: number }) => {
        if (data?.stargazers_count) setStars(data.stargazers_count)
      })
      .catch(() => {})
  }, [])

  if (stars === null) return null

  return (
    <a
      href={REPO_URL}
      target="_blank"
      rel="noreferrer"
      className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-3 py-1 font-mono text-[11px] text-muted-foreground transition-colors hover:border-signal hover:text-signal-ink"
    >
      <Star className="size-3 fill-signal text-signal" aria-hidden="true" />
      {stars >= 1000 ? `${(stars / 1000).toFixed(1).replace(/\.0$/, '')}k` : stars} stars
    </a>
  )
}
