'use client'

import { useEffect, useState } from 'react'
import { Star } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'

export function StarCount() {
  const [count, setCount] = useState<number | null>(null)

  useEffect(() => {
    fetch('https://api.github.com/repos/LukaG712/Evershade')
      .then((res) => {
        if (!res.ok) throw new Error('Failed')
        return res.json()
      })
      .then((data: { stargazers_count: number }) => {
        setCount(data.stargazers_count)
      })
      .catch(() => {
        // Silently fail — badge just won't show a count
      })
  }, [])

  if (count === null) return null

  return (
    <a
      href={REPO_URL}
      target="_blank"
      rel="noreferrer"
      className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background/60 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur-sm transition-colors hover:border-foreground/20 hover:text-foreground"
    >
      <Star className="size-3.5 fill-signal text-signal" aria-hidden="true" />
      <span>{count >= 1000 ? `${(count / 1000).toFixed(1).replace(/\.0$/, '')}k` : count} stars</span>
    </a>
  )
}
