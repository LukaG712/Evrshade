'use client'

import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

export const SUPPORTED_LOCALES = [
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'de', label: 'Deutsch', flag: '🇩🇪' },
  { code: 'es', label: 'Español', flag: '🇪🇸' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'pt', label: 'Português', flag: '🇧🇷' },
  { code: 'zh', label: '中文', flag: '🇨🇳' },
  { code: 'ja', label: '日本語', flag: '🇯🇵' },
  { code: 'ko', label: '한국어', flag: '🇰🇷' },
  { code: 'ru', label: 'Русский', flag: '🇷🇺' },
  { code: 'ar', label: 'العربية', flag: '🇸🇦' },
] as const

export type Locale = (typeof SUPPORTED_LOCALES)[number]['code']

const STORAGE_KEY = 'evershade-locale'

// English is inlined for SSR/hydration — other locales are lazy-loaded from JSON files.
import en from './locales/en.json'

const LOCALE_IMPORTS: Record<Locale, () => Promise<{ default: Record<string, string> }>> = {
  en: () => Promise.resolve({ default: en }),
  de: () => import('./locales/de.json'),
  es: () => import('./locales/es.json'),
  fr: () => import('./locales/fr.json'),
  pt: () => import('./locales/pt.json'),
  zh: () => import('./locales/zh.json'),
  ja: () => import('./locales/ja.json'),
  ko: () => import('./locales/ko.json'),
  ru: () => import('./locales/ru.json'),
  ar: () => import('./locales/ar.json'),
}

function getBrowserLocale(): Locale {
  const nav = typeof window !== 'undefined' ? navigator : null
  if (nav) {
    const codes = SUPPORTED_LOCALES.map(l => l.code)
    const browserLang = (nav.language || nav.languages?.[0] || 'en').slice(0, 2)
    if (codes.includes(browserLang)) return browserLang as Locale
  }
  return 'en'
}

function loadLocale(): Locale {
  if (typeof window === 'undefined') return 'en'
  const codes = SUPPORTED_LOCALES.map(l => l.code)
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored && codes.includes(stored)) return stored as Locale
  return getBrowserLocale()
}

interface I18nContextValue {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: string) => string
}

const I18nContext = createContext<I18nContextValue>({
  locale: 'en',
  setLocale: () => {},
  t: (key: string) => en[key] ?? key,
})

export function I18nProvider({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false)
  const [locale, setLocaleState] = useState<Locale>('en')
  const [dict, setDict] = useState<Record<string, string>>(en)

  useEffect(() => {
    const saved = loadLocale()
    setLocaleState(saved)
    document.documentElement.lang = saved
    // Load the locale dictionary if it's not English
    if (saved !== 'en') {
      LOCALE_IMPORTS[saved]().then(mod => {
        setDict(mod.default)
      })
    }
    setMounted(true)
  }, [])

  // During SSR and initial hydration, always render with 'en' to avoid mismatch.
  if (!mounted) {
    return (
      <I18nContext.Provider value={{ locale: 'en', setLocale: () => {}, t: (key: string) => en[key] ?? key }}>
        {children}
      </I18nContext.Provider>
    )
  }

  const handleSetLocale = (next: Locale) => {
    setLocaleState(next)
    localStorage.setItem(STORAGE_KEY, next)
    document.documentElement.lang = next
    document.documentElement.dir = next === 'ar' ? 'rtl' : 'ltr'
    if (next === 'en') {
      setDict(en)
    } else {
      LOCALE_IMPORTS[next]().then(mod => {
        setDict(mod.default)
      })
    }
  }

  const t = (key: string) => {
    return dict[key] ?? en[key] ?? key
  }

  return (
    <I18nContext.Provider value={{ locale, setLocale: handleSetLocale, t }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useI18n() {
  return useContext(I18nContext)
}
