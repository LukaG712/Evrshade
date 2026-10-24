'use client'

import { useEffect } from 'react'

export function PlausibleAnalytics({ domain }: { domain: string }) {
  useEffect(() => {
    // Set up Plausible
    ;(function () {
      const s = document.createElement('script')
      s.type = 'text/javascript'
      s.defer = true
      s.src = 'https://plausible.io/js/script.js'
      s.setAttribute('data-domain', domain)
      const head = document.getElementsByTagName('head')[0]
      if (head) head.appendChild(s)
    })()

    // Plausible trackPageView() will be available after the script loads
    window.addEventListener('pageshow', () => {
      if ((window as any).plausible) {
        ;(window as any).plausible('pageview')
      }
    })
  }, [domain])

  return null
}
