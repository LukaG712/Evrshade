'use client'

import { useEffect, useState } from 'react'

/**
 * Dramatic loading screen that plays once when the page loads,
 * then transitions into the main content.
 */
export function LoadingScreen() {
  const [visible, setVisible] = useState(true)
  const [progress, setProgress] = useState(0)
  const [fadeOut, setFadeOut] = useState(false)

  useEffect(() => {
    // Animate progress bar
    const duration = 1800
    const start = performance.now()
    let raf: number

    const tick = (now: number) => {
      const elapsed = now - start
      const p = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - p, 3)
      setProgress(eased)

      if (p < 1) {
        raf = requestAnimationFrame(tick)
      } else {
        // Hold for a moment, then fade out
        setTimeout(() => {
          setFadeOut(true)
          setTimeout(() => setVisible(false), 400)
        }, 300)
      }
    }

    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  if (!visible) return null

  return (
    <div
      className={`fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-background transition-opacity duration-400 ${
        fadeOut ? 'pointer-events-none opacity-0' : 'opacity-100'
      }`}
      aria-hidden={fadeOut}
    >
      {/* Logo mark */}
      <div className="mb-8 grid size-12 grid-cols-2 gap-px">
        <span className="bg-foreground" />
        <span className="bg-foreground" />
        <span className="bg-foreground" />
        <span className="bg-signal" />
      </div>

      {/* Brand name */}
      <h1 className="mb-8 font-semibold text-5xl tracking-[-0.05em] md:text-7xl">
        Evershade
        <span className="text-signal">.</span>
      </h1>

      {/* Progress bar */}
      <div className="h-px w-48 overflow-hidden bg-foreground/20">
        <div
          className="h-full bg-signal transition-none"
          style={{ width: `${progress * 100}%` }}
        />
      </div>

      {/* Progress text */}
      <p className="mt-3 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
        {Math.round(progress * 100)}%
      </p>
    </div>
  )
}
