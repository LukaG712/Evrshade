'use client'

import { useEffect } from 'react'

export function HapticFeedback() {
  useEffect(() => {
    const handleTouch = (e: TouchEvent) => {
      // Only vibrate on supported devices
      if (!navigator.vibrate) return

      const target = e.target as HTMLElement

      // Check if the touched element is a button, link, or interactive element
      const tag = target.tagName
      const role = target.getAttribute('role')
      const isInteractive =
        tag === 'BUTTON' ||
        tag === 'A' ||
        tag === 'INPUT' ||
        tag === 'SELECT' ||
        tag === 'SUMMARY' ||
        role === 'button' ||
        role === 'tab' ||
        role === 'menuitem' ||
        target.closest('button, a, [role="button"], [role="tab"]') !== null

      if (isInteractive) {
        navigator.vibrate(10)
      }
    }

    document.addEventListener('touchstart', handleTouch, { passive: true })
    return () => document.removeEventListener('touchstart', handleTouch)
  }, [])

  return null
}
