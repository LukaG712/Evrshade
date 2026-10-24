'use client'

import { useEffect, useRef, useState } from 'react'

type Heading = {
  id: string
  text: string
  level: number
}

export function BlogToc({ headings }: { headings: Heading[] }) {
  const [activeId, setActiveId] = useState('')
  const ref = useRef<HTMLUListElement>(null)

  useEffect(() => {
    if (headings.length === 0) return

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id)
          }
        }
      },
      { rootMargin: '-80px 0px -80% 0px' },
    )

    for (const h of headings) {
      const el = document.getElementById(h.id)
      if (el) observer.observe(el)
    }

    return () => observer.disconnect()
  }, [headings])

  if (headings.length === 0) return null

  return (
    <aside className="hidden xl:block xl:w-48 xl:shrink-0" aria-label="Table of contents">
      <nav className="sticky top-24">
        <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
          On this page
        </p>
        <ul ref={ref} className="mt-3 space-y-1 border-l border-border">
          {headings.map((h) => {
            const indent = h.level === 3 ? 'pl-3' : 'pl-2'
            const isActive = h.id === activeId
            return (
              <li key={h.id} className={indent}>
                <a
                  href={`#${h.id}`}
                  className={`block text-xs leading-snug transition-colors ${
                    isActive
                      ? 'border-signal border-l text-signal-ink'
                      : 'border-transparent border-l text-muted-foreground hover:text-foreground'
                  }`}
                  style={{ paddingLeft: h.level === 3 ? '0.75rem' : '0.5rem' }}
                >
                  {h.text}
                </a>
              </li>
            )
          })}
        </ul>
      </nav>
    </aside>
  )
}
