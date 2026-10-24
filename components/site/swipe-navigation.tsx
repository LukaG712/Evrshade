'use client'

import { useEffect, useRef } from 'react'

const SECTIONS = [
  'top',
  'overview',
  'how-it-works',
  'platform',
  'get-started',
  'about',
  'roadmap',
]

export function SwipeNavigation() {
  const touchStartX = useRef(0)
  const touchStartY = useRef(0)
  const currentSection = useRef(0)

  useEffect(() => {
    const onTouchStart = (e: TouchEvent) => {
      touchStartX.current = e.touches[0].clientX
      touchStartY.current = e.touches[0].clientY
      // Detect current section on swipe start
      const scrollY = window.scrollY + window.innerHeight / 2
      for (let i = SECTIONS.length - 1; i >= 0; i--) {
        const el = document.getElementById(SECTIONS[i]) || document.querySelector(`[id$="-${SECTIONS[i]}"]`)
        if (el && el.getBoundingClientRect().top <= scrollY - window.innerHeight / 2) {
          currentSection.current = i
          break
        }
      }
    }

    const onTouchEnd = (e: TouchEvent) => {
      const dx = e.changedTouches[0].clientX - touchStartX.current
      const dy = e.changedTouches[0].clientY - touchStartY.current

      // Only handle horizontal swipes (ignore vertical scrolling)
      if (Math.abs(dx) < 60 || Math.abs(dx) < Math.abs(dy)) return

      // Haptic feedback on supported devices
      if (navigator.vibrate) navigator.vibrate(10)

      if (dx < 0 && currentSection.current < SECTIONS.length - 1) {
        // Swipe left → next section
        currentSection.current++
      } else if (dx > 0 && currentSection.current > 0) {
        // Swipe right → previous section
        currentSection.current--
      }

      const target = document.getElementById(SECTIONS[currentSection.current])
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' })
      }
    }

    document.addEventListener('touchstart', onTouchStart, { passive: true })
    document.addEventListener('touchend', onTouchEnd, { passive: true })
    return () => {
      document.removeEventListener('touchstart', onTouchStart)
      document.removeEventListener('touchend', onTouchEnd)
    }
  }, [])

  return null
}
