'use client'

import { useEffect, useRef } from 'react'

export function ReadingProgress() {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const bar = ref.current
    if (!bar) return

    let ticking = false
    const onScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          if (!bar) return
          const docHeight = document.documentElement.scrollHeight - window.innerHeight
          if (docHeight <= 0) return
          const progress = Math.min((window.scrollY / docHeight) * 100, 100)
          bar.style.width = `${progress}%`
          ticking = false
        })
        ticking = true
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div className="fixed left-0 top-16 z-50 h-0.5 bg-signal" ref={ref} style={{ width: '0%', willChange: 'width' }} />
  )
}
