import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { HapticFeedback } from '@/components/site/haptic-feedback'
import { PageTransition } from '@/components/site/page-transition'
import './globals.css'

const geist = Geist({ subsets: ['latin'], variable: '--font-geist' })
const geistMono = Geist_Mono({ subsets: ['latin'], variable: '--font-geist-mono' })

export const metadata: Metadata = {
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
}

export const viewport: Viewport = {
  colorScheme: 'light dark',
  themeColor: [{ media: '(prefers-color-scheme: light)', color: '#fcfcfa' }, { media: '(prefers-color-scheme: dark)', color: '#242422' }],
  viewportFit: 'cover',
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'Evershade',
  description: 'Self-hosted AI agent platform built as a collection of specialized microservices.',
  applicationCategory: 'DeveloperApplication',
  operatingSystem: 'Linux, macOS, Windows',
  offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
  author: { '@type': 'Person', name: 'LukaG712', url: 'https://github.com/LukaG712' },
  license: 'https://opensource.org/licenses/MIT',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={`${geist.variable} ${geistMono.variable}`}>
      <body className="antialiased" suppressHydrationWarning>
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
        <HapticFeedback />
        <PageTransition>{children}</PageTransition>
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
