'use client'

import { useEffect, useRef } from 'react'

export function ScrollProgress() {
  const barRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const bar = barRef.current
    if (!bar) return

    let ticking = false
    const onScroll = () => {
      if (!ticking) {
        ticking = true
        requestAnimationFrame(() => {
          const scrollTop = window.scrollY
          const docHeight = document.documentElement.scrollHeight - window.innerHeight
          const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0
          bar.style.width = `${pct}%`
          ticking = false
        })
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div
      ref={barRef}
      className="fixed top-0 left-0 z-50 h-0.5 bg-signal"
      style={{ width: '0%' }}
      aria-hidden="true"
    />
  )
}
