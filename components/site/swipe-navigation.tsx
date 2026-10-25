'use client'

import { useEffect, useRef } from 'react'

const SECTIONS = [
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

  useEffect(() => {
    const onTouchStart = (e: TouchEvent) => {
      touchStartX.current = e.touches[0].clientX
      touchStartY.current = e.touches[0].clientY
    }

    const onTouchEnd = (e: TouchEvent) => {
      const endX = e.changedTouches[0].clientX
      const endY = e.changedTouches[0].clientY
      const deltaX = endX - touchStartX.current
      const deltaY = Math.abs(endY - touchStartY.current)

      // Only trigger if horizontal swipe is dominant and exceeds threshold
      if (Math.abs(deltaX) < 60 || deltaY > Math.abs(deltaX)) return

      const currentSection = getCurrentSection()

      if (deltaX < 0 && currentSection < SECTIONS.length - 1) {
        // Swipe left → next section
        const target = document.getElementById(SECTIONS[currentSection + 1])
        target?.scrollIntoView({ behavior: 'auto' })
      } else if (deltaX > 0 && currentSection > 0) {
        // Swipe right → previous section
        const target = document.getElementById(SECTIONS[currentSection - 1])
        target?.scrollIntoView({ behavior: 'auto' })
      }
    }

    const getCurrentSection = () => {
      let current = 0
      for (let i = SECTIONS.length - 1; i >= 0; i--) {
        const el = document.getElementById(SECTIONS[i])
        if (el && el.getBoundingClientRect().top <= 100) {
          current = i
          break
        }
      }
      return current
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
