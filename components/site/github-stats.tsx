'use client'

import { useEffect, useState } from 'react'
import { Star, GitFork } from 'lucide-react'

export function GithubStats() {
  const [stars, setStars] = useState<number | null>(null)
  const [forks, setForks] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('https://api.github.com/repos/LukaG712/Evershade')
      .then((res) => res.json())
      .then((data) => {
        setStars(data.stargazers_count ?? null)
        setForks(data.forks_count ?? null)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center gap-6">
        <div className="h-8 w-24 animate-pulse rounded bg-muted" />
        <div className="h-8 w-24 animate-pulse rounded bg-muted" />
      </div>
    )
  }

  return (
    <div className="flex items-center gap-6">
      <div className="flex items-center gap-2">
        <Star className="size-4 text-signal" aria-hidden="true" />
        <span className="text-2xl font-semibold tabular-nums">
          {stars !== null ? stars.toLocaleString() : '—'}
        </span>
        <span className="text-sm text-muted-foreground">Stars</span>
      </div>
      <div className="flex items-center gap-2">
        <GitFork className="size-4 text-muted-foreground" aria-hidden="true" />
        <span className="text-2xl font-semibold tabular-nums">
          {forks !== null ? forks.toLocaleString() : '—'}
        </span>
        <span className="text-sm text-muted-foreground">Forks</span>
      </div>
    </div>
  )
}
