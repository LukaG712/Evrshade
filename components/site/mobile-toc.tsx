'use client'

import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useI18n } from '@/lib/i18n'

const NAV_KEYS = [
  { href: '#overview', key: 'nav.overview' },
  { href: '#how-it-works', key: 'nav.how-it-works' },
  { href: '#platform', key: 'nav.platform' },
  { href: '#get-started', key: 'nav.get-started' },
  { href: '#about', key: 'nav.about' },
  { href: '#roadmap', key: 'nav.roadmap' },
] as const

export function MobileToc() {
  const { t } = useI18n()
  const [activeIndex, setActiveIndex] = useState(0)
  const [offset, setOffset] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)
  const activeIndexRef = useRef(0)

  useEffect(() => {
    let ticking = false
    let rafId = 0

    const onScroll = () => {
      if (!ticking) {
        ticking = true
        rafId = requestAnimationFrame(() => {
          // Find the current section based on scroll position
          let current = 0
          for (let i = NAV_KEYS.length - 1; i >= 0; i--) {
            const el = document.getElementById(NAV_KEYS[i].href.slice(1))
            if (el) {
              const rect = el.getBoundingClientRect()
              if (rect.top <= 200) {
                current = i
                break
              }
            }
          }
          // Only update React state when the active section actually changes
          if (current !== activeIndexRef.current) {
            activeIndexRef.current = current
            setActiveIndex(current)

            // Auto-scroll the container to keep active item visible
            const container = containerRef.current
            if (container) {
              const itemWidth = 100
              const containerWidth = container.clientWidth
              const idealOffset = current * itemWidth - containerWidth / 2 + itemWidth / 2
              const maxOffset = Math.max(0, NAV_KEYS.length * itemWidth - containerWidth)
              setOffset(Math.min(maxOffset, Math.max(0, idealOffset)))
            }
          }
          ticking = false
        })
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => {
      window.removeEventListener('scroll', onScroll)
      cancelAnimationFrame(rafId)
    }
  }, [])

  const scrollTo = (href: string) => {
    const el = document.getElementById(href.slice(1))
    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - 64
      window.scrollTo({ top: y, behavior: 'smooth' })
    }
  }

  const canScrollLeft = offset > 0
  const canScrollRight = offset < Math.max(0, NAV_KEYS.length * 100 - (containerRef.current?.clientWidth ?? 300))

  const scroll = (direction: 'left' | 'right') => {
    setOffset(prev => {
      const delta = direction === 'left' ? -100 : 100
      const maxOffset = Math.max(0, NAV_KEYS.length * 100 - (containerRef.current?.clientWidth ?? 300))
      return Math.min(maxOffset, Math.max(0, prev + delta))
    })
  }

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-background/95 backdrop-blur md:hidden"
      aria-label="Table of contents"
    >
      <div className="flex items-center h-14">
        {canScrollLeft && (
          <button
            onClick={() => scroll('left')}
            className="flex-shrink-0 px-2 text-muted-foreground hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2"
            aria-label={t('mobile-toc.scroll-left')}
            type="button"
          >
            <ChevronLeft className="size-4" />
          </button>
        )}
        <div
          ref={containerRef}
          className="flex-1 overflow-hidden px-1"
        >
          <div
            className="flex gap-1"
            style={{ transform: `translateX(-${offset}px)`, transition: 'transform 0.3s ease' }}
          >
            {NAV_KEYS.map((section, i) => {
              const isActive = i === activeIndex
              return (
                <button
                  key={section.href}
                  onClick={() => scrollTo(section.href)}
                  className={`flex-shrink-0 px-3 py-1.5 text-xs font-medium transition-colors rounded-md ${
                    isActive
                      ? 'bg-signal/10 text-signal'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  }`}
                  aria-current={isActive ? 'true' : undefined}
                  type="button"
                >
                  {t(section.key)}
                </button>
              )
            })}
          </div>
        </div>
        {canScrollRight && (
          <button
            onClick={() => scroll('right')}
            className="flex-shrink-0 px-2 text-muted-foreground hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2"
            aria-label={t('mobile-toc.scroll-right')}
            type="button"
          >
            <ChevronRight className="size-4" />
          </button>
        )}
      </div>
    </nav>
  )
}
