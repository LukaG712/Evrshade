'use client'

import { useEffect, useState } from 'react'
import { MessageCircle } from 'lucide-react'

export function DiscordWidget() {
  const [members, setMembers] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch Discord widget data (requires server intent enabled on the Discord server)
    fetch('https://discord.com/api/guilds/1234567890/widget.json')
      .then((res) => {
        if (res.ok) return res.json()
        throw new Error('Not found')
      })
      .then((data) => {
        setMembers(data.presence_count ?? data.member_count ?? null)
        setLoading(false)
      })
      .catch(() => {
        // Fallback: just hide the member count
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        <MessageCircle className="size-4 text-muted-foreground" aria-hidden="true" />
        <div className="h-4 w-16 animate-pulse rounded bg-muted" />
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <MessageCircle className="size-4 text-signal" aria-hidden="true" />
      <span className="text-sm text-muted-foreground">
        {members !== null ? `${members} online` : 'Join Discord'}
      </span>
    </div>
  )
}
