'use client'

import { useEffect, useState } from 'react'
import { REPO_URL } from '@/lib/evershade'

type Contributor = {
  login: string
  avatar_url: string
  contributions: number
}

export function ContributorAvatars() {
  const [contributors, setContributors] = useState<Contributor[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('https://api.github.com/repos/LukaG712/Evershade/contributors?per_page=12')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setContributors(data.slice(0, 12))
        }
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="size-8 animate-pulse rounded-full bg-muted" />
        ))}
      </div>
    )
  }

  if (contributors.length === 0) return null

  return (
    <div>
      <div className="flex items-center -space-x-2">
        {contributors.map((c) => (
          <a
            key={c.login}
            href={`${REPO_URL}/graph/contributors`}
            target="_blank"
            rel="noreferrer"
            className="size-8 rounded-full border-2 border-background transition-transform hover:scale-110 hover:z-10"
            aria-label={`${c.login} (${c.contributions} contributions)`}
            title={`${c.login} (${c.contributions} contributions)`}
          >
            <img
              src={c.avatar_url}
              alt={c.login}
              className="size-8 rounded-full"
              loading="lazy"
              width={32}
              height={32}
            />
          </a>
        ))}
      </div>
      <p className="mt-2 text-xs text-muted-foreground">
        {contributors.length} contributor{contributors.length !== 1 ? 's' : ''}
      </p>
    </div>
  )
}
