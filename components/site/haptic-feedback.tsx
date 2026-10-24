'use client'

import { useEffect } from 'react'

export function HapticFeedback() {
  useEffect(() => {
    const handler = (e: Event) => {
      const target = e.target as HTMLElement
      if (!target.closest('button, a, [role="button"], input, select, textarea')) return
      if (typeof navigator !== 'undefined' && navigator.vibrate) {
        navigator.vibrate(10)
      }
    }

    document.addEventListener('pointerdown', handler, { passive: true })
    return () => document.removeEventListener('pointerdown', handler)
  }, [])

  return null
}
