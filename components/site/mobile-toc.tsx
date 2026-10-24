'use client'

import { useEffect, useRef, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

const SECTIONS = [
  { label: 'Home', href: '#top' },
  { label: 'Overview', href: '#overview' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Platform', href: '#platform' },
  { label: 'Get Started', href: '#get-started' },
  { label: 'About', href: '#about' },
  { label: 'Roadmap', href: '#roadmap' },
]

export function MobileToc() {
  const [active, setActive] = useState(0)
  const [overflow, setOverflow] = useState({ left: true, right: true })
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let raf = 0
    let lastActive = 0
    const update = () => {
      raf = 0
      const sections = SECTIONS.slice(1).map((s) => document.querySelector(s.href))
      let current = 0
      for (let i = 0; i < sections.length; i++) {
        const el = sections[i]
        if (el && el.getBoundingClientRect().top <= 100) {
          current = i + 1
        }
      }
      if (current !== lastActive) {
        lastActive = current
        setActive(current)
      }
    }
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const scroll = (dir: 'left' | 'right') => {
    const el = scrollRef.current
    if (!el) return
    el.scrollBy({ left: dir === 'left' ? -120 : 120, behavior: 'smooth' })
  }

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    const check = () => {
      setOverflow({
        left: el.scrollLeft > 5,
        right: el.scrollLeft < el.scrollWidth - el.clientWidth - 5,
      })
    }
    check()
    el.addEventListener('scroll', check)
    return () => el.removeEventListener('scroll', check)
  }, [])

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-50 border-t border-border bg-background/90 backdrop-blur-md md:hidden"
      style={{ paddingBottom: 'env(safe-area-inset-bottom, 0)' }}
      aria-label="Mobile navigation"
    >
      <div className="relative flex items-center">
        {overflow.left && (
          <button
            type="button"
            onClick={() => scroll('left')}
            className="absolute left-0 z-10 flex h-10 w-8 items-center justify-center bg-gradient-to-r from-background to-transparent"
            aria-label="Scroll left"
          >
            <ChevronLeft className="size-4" />
          </button>
        )}
        <div
          ref={scrollRef}
          className="flex flex-1 overflow-x-auto px-2 py-1.5 scrollbar-hide"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {SECTIONS.map((section, i) => (
            <a
              key={section.href}
              href={section.href}
              className={`flex shrink-0 items-center rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
                i === active
                  ? 'bg-signal/10 text-signal-ink'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {section.label}
            </a>
          ))}
        </div>
        {overflow.right && (
          <button
            type="button"
            onClick={() => scroll('right')}
            className="absolute right-0 z-10 flex h-10 w-8 items-center justify-center bg-gradient-to-l from-background to-transparent"
            aria-label="Scroll right"
          >
            <ChevronRight className="size-4" />
          </button>
        )}
      </div>
    </nav>
  )
}
