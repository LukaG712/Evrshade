'use client'

import { Globe, Check } from 'lucide-react'
import { useState } from 'react'
import { SUPPORTED_LOCALES, useI18n, type Locale } from '@/lib/i18n'

export function LanguageSelector({ className }: { className?: string }) {
  const { locale, setLocale, t } = useI18n()
  const [open, setOpen] = useState(false)
  const current = SUPPORTED_LOCALES.find(l => l.code === locale)

  return (
    <div className={`relative ${className ?? ''}`}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="inline-flex h-8 items-center gap-1.5 rounded-sm border border-border px-2.5 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:border-foreground/20 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2"
        aria-label={t('header.toggle-menu')}
        aria-expanded={open}
      >
        <Globe className="size-3.5" aria-hidden="true" />
        <span className="hidden sm:inline">{current?.flag}</span>
      </button>
      {open && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
            aria-hidden="true"
          />
          <div className="absolute right-0 z-50 mt-2 min-w-[160px] rounded-sm border border-border bg-background shadow-lg">
            <ul className="py-1">
              {SUPPORTED_LOCALES.map((lang) => (
                <li key={lang.code}>
                  <button
                    type="button"
                    className={`flex w-full items-center gap-2 px-3 py-2 text-sm transition-colors hover:bg-muted ${
                      locale === lang.code ? 'text-signal' : 'text-foreground'
                    }`}
                    onClick={() => {
                      setLocale(lang.code)
                      setOpen(false)
                    }}
                  >
                    <span className="text-base">{lang.flag}</span>
                    <span className="flex-1 text-left">{lang.label}</span>
                    {locale === lang.code && (
                      <Check className="size-3.5 text-signal" aria-hidden="true" />
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  )
}
