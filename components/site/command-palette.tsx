'use client'

import { Command, X } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useI18n } from '@/lib/i18n'

const SECTIONS = [
  { id: 'overview', label: 'Overview', category: 'Sections' },
  { id: 'how-it-works', label: 'How It Works', category: 'Sections' },
  { id: 'platform', label: 'Platform', category: 'Sections' },
  { id: 'get-started', label: 'Get Started', category: 'Sections' },
  { id: 'about', label: 'About', category: 'Sections' },
  { id: 'roadmap', label: 'Roadmap', category: 'Sections' },
  { id: 'services', label: 'Services Grid', category: 'Sections' },
  { id: 'mission-console', label: 'Mission Console', category: 'Sections' },
  { id: 'architecture', label: 'Architecture', category: 'Sections' },
  { id: 'security', label: 'Security', category: 'Sections' },
  { id: 'download', label: 'Download', category: 'Sections' },
  { id: 'system-requirements', label: 'System Requirements', category: 'Sections' },
  { id: 'comparison', label: 'Comparison', category: 'Sections' },
  { id: 'changelog', label: 'Changelog', category: 'Sections' },
  { id: 'community', label: 'Community', category: 'Sections' },
  { id: 'contributing', label: 'Contributing', category: 'Sections' },
  { id: 'faq', label: 'FAQ', category: 'Sections' },
  { id: 'glossary', label: 'Glossary', category: 'Sections' },
  { id: 'integrations', label: 'Integrations', category: 'Sections' },
  { id: 'api-reference', label: 'API Reference', category: 'Sections' },
  { id: 'cli', label: 'CLI', category: 'Sections' },
  { id: 'docker-compose', label: 'Docker Compose', category: 'Sections' },
  { id: 'performance', label: 'Performance', category: 'Sections' },
  { id: 'testimonials', label: 'Testimonials', category: 'Sections' },
  { id: 'migration', label: 'Migration Guide', category: 'Sections' },
] as const

export function CommandPalette() {
  const { t } = useI18n()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const toggle = useCallback(() => {
    setOpen(prev => {
      const next = !prev
      if (next) {
        setQuery('')
        setSelectedIndex(0)
        setTimeout(() => inputRef.current?.focus(), 50)
      }
      return next
    })
  }, [])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        toggle()
      }
      if (e.key === 'Escape' && open) {
        e.preventDefault()
        setOpen(false)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, toggle])

  useEffect(() => {
    if (open) {
      setQuery('')
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [open])

  const filtered = SECTIONS.filter(s =>
    s.label.toLowerCase().includes(query.toLowerCase())
  )

  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex(prev => Math.min(prev + 1, filtered.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex(prev => Math.max(prev - 1, 0))
    } else if (e.key === 'Enter' && filtered[selectedIndex]) {
      e.preventDefault()
      navigateTo(filtered[selectedIndex].id)
    }
  }

  const navigateTo = (id: string) => {
    setOpen(false)
    // Try exact ID first, then look for elements containing the ID
    let el = document.getElementById(id)
    if (!el) {
      // Try finding by data attribute or class
      el = document.querySelector(`[id*="${id}"]`) as HTMLElement | null
    }
    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - 64
      window.scrollTo({ top: y, behavior: 'smooth' })
    }
  }

  // Group by category
  const groups: Record<string, typeof SECTIONS> = {}
  filtered.forEach(s => {
    if (!groups[s.category]) groups[s.category] = []
    groups[s.category].push(s)
  })

  return (
    <>
      {/* Keyboard shortcut hint in header */}
      <button
        onClick={toggle}
        type="button"
        className="hidden lg:flex items-center gap-2 rounded-sm border border-border px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:border-foreground/20 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2"
        aria-label="Open command palette"
      >
        <Command className="size-3.5" />
        <span>{t('header.search')}</span>
        <kbd className="ml-2 inline-flex items-center gap-0.5 rounded-sm border border-border bg-muted px-1.5 py-0.5 font-mono text-[10px]">
          Ctrl+K
        </kbd>
      </button>

      {/* Modal overlay */}
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]"
          onClick={e => { if (e.target === e.currentTarget) setOpen(false) }}
        >
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm" />
          <div
            ref={containerRef}
            className="relative z-10 w-full max-w-lg border border-border bg-background shadow-lg"
            onKeyDown={handleKeyDown}
          >
            {/* Header */}
            <div className="flex items-center gap-3 border-b border-border px-4">
              <Command className="size-4 text-muted-foreground" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder={t('command-palette.placeholder')}
                className="flex-1 py-3 text-sm outline-none placeholder:text-muted-foreground"
              />
              <button
                onClick={() => setOpen(false)}
                type="button"
                className="rounded-sm p-1 text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2"
                aria-label="Close"
              >
                <X className="size-4" />
              </button>
            </div>

            {/* Results */}
            <div className="max-h-[60vh] overflow-y-auto p-2">
              {filtered.length === 0 ? (
                <p className="py-8 text-center text-sm text-muted-foreground">
                  {t('command-palette.no-results')}
                </p>
              ) : (
                Object.entries(groups).map(([category, items]) => (
                  <div key={category} className="mb-2">
                    <p className="px-2 py-1.5 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                      {category}
                    </p>
                    {items.map((item, i) => {
                      const globalIndex = SECTIONS.findIndex(s => s.id === item.id)
                      const isSelected = globalIndex === selectedIndex
                      return (
                        <button
                          key={item.id}
                          onClick={() => navigateTo(item.id)}
                          className={`w-full rounded-sm px-3 py-2 text-left text-sm transition-colors ${
                            isSelected
                              ? 'bg-muted text-foreground'
                              : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                          }`}
                        >
                          {item.label}
                        </button>
                      )
                    })}
                  </div>
                ))
              )}
            </div>

            {/* Footer hint */}
            <div className="flex items-center justify-between border-t border-border px-4 py-2">
              <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                <span className="flex items-center gap-1">
                  <kbd className="rounded-sm border border-border px-1 py-0.5 font-mono">↑↓</kbd>
                  <span>navigate</span>
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="rounded-sm border border-border px-1 py-0.5 font-mono">↵</kbd>
                  <span>open</span>
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="rounded-sm border border-border px-1 py-0.5 font-mono">esc</kbd>
                  <span>close</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
