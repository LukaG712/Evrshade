'use client'

import { useEffect, useRef, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

const SECTIONS = [
  { id: 'overview', label: 'Overview' },
  { id: 'how-it-works', label: 'How It Works' },
  { id: 'platform', label: 'Platform' },
  { id: 'get-started', label: 'Get Started' },
  { id: 'about', label: 'About' },
  { id: 'roadmap', label: 'Roadmap' },
]

export function MobileToc() {
  const [active, setActive] = useState(0)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let ticking = false

    const onScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          let current = 0
          for (let i = SECTIONS.length - 1; i >= 0; i--) {
            const el = document.getElementById(SECTIONS[i].id)
            if (el && el.getBoundingClientRect().top <= 100) {
              current = i
              break
            }
          }
          setActive(current)
          ticking = false
        })
        ticking = true
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const scroll = (dir: 'left' | 'right') => {
    const el = scrollRef.current
    if (el) el.scrollBy({ left: dir === 'left' ? -120 : 120, behavior: 'smooth' })
  }

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-background/80 backdrop-blur-lg md:hidden"
      aria-label="Mobile navigation"
    >
      <div className="flex items-center h-12">
        <button
          type="button"
          onClick={() => scroll('left')}
          className="flex-shrink-0 px-2 text-muted-foreground active:scale-95"
          aria-label="Scroll left"
        >
          <ChevronLeft className="size-4" />
        </button>
        <div
          ref={scrollRef}
          className="flex-1 overflow-x-auto scrollbar-hide px-1"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          <div className="flex gap-0.5 px-1">
            {SECTIONS.map((section, i) => (
              <a
                key={section.id}
                href={`#${section.id}`}
                className={`flex-shrink-0 px-3 py-1.5 text-xs font-medium rounded-full transition-colors ${
                  i === active
                    ? 'bg-signal/15 text-signal-ink'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {section.label}
              </a>
            ))}
          </div>
        </div>
        <button
          type="button"
          onClick={() => scroll('right')}
          className="flex-shrink-0 px-2 text-muted-foreground active:scale-95"
          aria-label="Scroll right"
        >
          <ChevronRight className="size-4" />
        </button>
      </div>
    </nav>
  )
}
