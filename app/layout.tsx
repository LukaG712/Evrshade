import type { Metadata, Viewport } from 'next'
import Script from 'next/script'
import { Geist, Geist_Mono } from 'next/font/google'
import { I18nProvider } from '@/lib/i18n'
import { ServiceWorkerRegister } from '@/components/site/service-worker-register'
import { PlausibleAnalytics } from '@/components/site/plausible-analytics'
import './globals.css'

const geist = Geist({ subsets: ['latin'], variable: '--font-geist' })
const geistMono = Geist_Mono({ subsets: ['latin'], variable: '--font-geist-mono' })

export const metadata: Metadata = {
  metadataBase: new URL('https://evrshade.netlify.app'),
  title: 'Evershade: Self-hosted AI agent platform',
  description:
    'Evershade is a self-hosted AI agent platform built as a collection of specialized microservices. Orchestrate agents, run missions, and own your data.',
  generator: 'v0.app',
  keywords: [
    'AI agent',
    'self-hosted',
    'microservices',
    'mission control',
    'code automation',
    'LLM orchestration',
    'SQLite',
    'Docker',
  ],
  authors: [{ name: 'LukaG712', url: 'https://github.com/LukaG712' }],
  creator: 'LukaG712',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://evrshade.netlify.app',
    title: 'Evershade: Self-hosted AI agent platform',
    description:
      'Orchestrate AI agents, run missions, and own your data. 10 modular microservices, SQLite-first, no heavy infrastructure.',
    siteName: 'Evershade',
    images: [
      {
        url: '/og.png',
        width: 1200,
        height: 630,
        alt: 'Evershade — Self-hosted AI agent platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Evershade: Self-hosted AI agent platform',
    description:
      'Orchestrate AI agents, run missions, and own your data. 10 modular microservices, SQLite-first, no heavy infrastructure.',
    images: ['/og.png'],
  },
  icons: {
    icon: [
      { url: '/icon-light-32x32.png', media: '(prefers-color-scheme: light)' },
      { url: '/icon-dark-32x32.png', media: '(prefers-color-scheme: dark)' },
      { url: '/icon.svg', type: 'image/svg+xml' },
    ],
    apple: '/apple-icon.png',
  },
  manifest: '/site.webmanifest',
  alternates: {
    types: {
      'application/rss+xml': [
        { url: '/api/releases', title: 'Evershade Release Feed' },
      ],
    },
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  colorScheme: 'light dark',
  themeColor: [{ media: '(prefers-color-scheme: light)', color: '#fcfcfa' }, { media: '(prefers-color-scheme: dark)', color: '#1a1a2e' }],
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'Evershade',
  description: 'Self-hosted AI agent platform built as a collection of specialized microservices. Orchestrate agents, run missions, and own your data.',
  url: 'https://evrshade.netlify.app',
  image: 'https://evrshade.netlify.app/og.png',
  softwareVersion: '0.1.0',
  operatingSystem: 'Linux, macOS, Windows',
  applicationCategory: 'DeveloperApplication',
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
  },
  license: 'https://opensource.org/licenses/MIT',
  author: {
    '@type': 'Person',
    name: 'LukaG712',
    url: 'https://github.com/LukaG712',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const plausibleDomain = process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN
  return (
    <html lang="en" className={`${geist.variable} ${geistMono.variable}`}>
      <head>
        <Script
          id="json-ld"
          type="application/ld+json"
          strategy="afterInteractive"
        >
          {JSON.stringify(jsonLd)}
        </Script>
      </head>
      <body className="antialiased">
        <I18nProvider>
          {children}
        </I18nProvider>
        <ServiceWorkerRegister />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#fcfcfa" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        {plausibleDomain && <PlausibleAnalytics domain={plausibleDomain} />}
      </body>
    </html>
  )
}
