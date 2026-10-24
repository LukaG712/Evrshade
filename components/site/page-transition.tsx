'use client'

import { useEffect, useState } from 'react'

export function PageTransition({ children }: { children: React.ReactNode }) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Small delay to ensure the transition triggers
    const timer = setTimeout(() => setIsVisible(true), 50)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div
      className={`transition-opacity duration-300 ease-in ${isVisible ? 'opacity-100' : 'opacity-0'}`}
    >
      {children}
    </div>
  )
}
