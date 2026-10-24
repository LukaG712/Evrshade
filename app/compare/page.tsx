'use client'

import { Check, X, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { useI18n } from '@/lib/i18n'

const CATEGORIES = [
  {
    name: 'Core',
    features: [
      { feature: 'Self-hosted', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
      { feature: 'No cloud dependency', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
      { feature: 'Runs on dev hardware', evershade: true, cursor: true, copilot: true, aider: true, opendevin: true },
      { feature: 'Modular microservices', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Multi-agent orchestration', evershade: true, cursor: false, copilot: false, aider: false, opendevin: true },
      { feature: 'Mission-based workflows', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Web dashboard', evershade: true, cursor: true, copilot: false, aider: false, opendevin: true },
      { feature: 'CLI interface', evershade: true, cursor: false, copilot: false, aider: true, opendevin: false },
      { feature: 'REST API', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
    ],
  },
  {
    name: 'Security',
    features: [
      { feature: 'Approval gates', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Sandboxed execution', evershade: true, cursor: false, copilot: false, aider: false, opendevin: true },
      { feature: 'Secrets encryption (AES-256)', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Prompt injection defense', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Autonomy dial (safety levels)', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'No telemetry', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
    ],
  },
  {
    name: 'Memory & Knowledge',
    features: [
      { feature: 'Knowledge graph memory', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Persistent agent memory', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Semantic search', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Context window management', evershade: true, cursor: true, copilot: true, aider: true, opendevin: true },
    ],
  },
  {
    name: 'Observability',
    features: [
      { feature: 'Built-in metrics', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Distributed tracing', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Structured logging', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Request trace visualization', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Performance dashboards', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
    ],
  },
  {
    name: 'Architecture',
    features: [
      { feature: 'SQLite-first storage', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Docker Compose deploy', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
      { feature: 'No Kubernetes required', evershade: true, cursor: true, copilot: true, aider: true, opendevin: true },
      { feature: 'Plugin system', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Event-driven architecture', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'Webhook integrations', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
    ],
  },
  {
    name: 'Models & Providers',
    features: [
      { feature: 'Bring your own API key', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
      { feature: 'Multi-provider support', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
      { feature: 'Local model support (Ollama)', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
      { feature: 'Model routing', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
      { feature: 'No vendor lock-in', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
    ],
  },
  {
    name: 'Cost',
    features: [
      { feature: 'Free (MIT license)', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
      { feature: 'No subscription required', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
      { feature: 'No credit system', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
      { feature: 'No rate limits', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
      { feature: 'Pay only for API calls', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
    ],
  },
] as const

const WHY_CARDS = [
  {
    title: 'Why security matters',
    body: 'Evershade ships with approval gates, sandboxed execution, encrypted secrets, and prompt injection defense. Nothing runs without your say-so, and you can dial autonomy up or down at any time.',
  },
  {
    title: 'Why observability matters',
    body: 'Built-in metrics, distributed tracing, and structured logging mean you always know what your agents are doing. No external tools or subscriptions needed — it just works.',
  },
  {
    title: 'Why modularity matters',
    body: '10 independent microservices you can mix and match. Run just the core orchestrator, or add observability, notifications, a knowledge graph, and a web dashboard as you need them.',
  },
  {
    title: 'Why your data matters',
    body: 'Knowledge graph memory, persistent agent state, and semantic search — all stored locally in SQLite. Your data never leaves your machine unless you explicitly send it to an API.',
  },
] as const

export default function ComparePage() {
  const { t } = useI18n()

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Hero */}
      <div className="relative border-b border-border pt-32 pb-16 px-4 md:pt-40 md:pb-20 md:px-[max(24px,3vw)]">
        <div className="absolute inset-0 bg-[length:32px_32px] bg-grid" aria-hidden="true" />
        <div className="relative">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="size-4" />
            {t('compare.back')}
          </Link>
          <h1 className="mt-8 text-4xl font-semibold tracking-tight md:text-6xl">
            {t('compare.title')}<span className="text-signal">.</span>
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
            {t('compare.lead')}
          </p>
          <p className="mt-2 font-mono text-[10px] text-muted-foreground">
            {t('compare.disclaimer')}
          </p>
        </div>
      </div>

      {/* Summary scores */}
      <div className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-20">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">
          {t('compare.summary')}
        </p>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {[
            { name: 'Evershade', total: CATEGORIES.reduce((sum, cat) => sum + cat.features.length, 0), color: 'border-signal bg-signal/5' },
            { name: 'Cursor', total: CATEGORIES.reduce((sum, cat) => sum + cat.features.filter(f => f.cursor).length, 0) },
            { name: 'Copilot', total: CATEGORIES.reduce((sum, cat) => sum + cat.features.filter(f => f.copilot).length, 0) },
            { name: 'Aider', total: CATEGORIES.reduce((sum, cat) => sum + cat.features.filter(f => f.aider).length, 0) },
            { name: 'OpenDevin', total: CATEGORIES.reduce((sum, cat) => sum + cat.features.filter(f => f.opendevin).length, 0) },
          ].map((item) => (
            <div
              key={item.name}
              className={`rounded-sm border p-5 text-center transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${
                item.color || 'border-border'
              }`}
            >
              <p className={`text-sm font-medium ${item.name === 'Evershade' ? 'text-signal-ink' : 'text-muted-foreground'}`}>
                {item.name}
              </p>
              <p className={`mt-3 text-3xl font-semibold tracking-tight ${item.name === 'Evershade' ? 'text-signal-ink' : ''}`}>
                {item.name === 'Evershade' ? item.total : `${item.total}/${item.total}`}
              </p>
              <p className="mt-2 font-mono text-[10px] text-muted-foreground">
                {t('compare.features-count')}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Category tables */}
      <div className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-20">
        {CATEGORIES.map((category) => (
          <div key={category.name} className="mb-16 md:mb-20">
            <h2 className="text-2xl font-semibold tracking-tight md:text-3xl">
              {category.name}
            </h2>
            <div className="mt-6 overflow-x-auto border-t border-foreground">
              <table className="w-full min-w-[640px] text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="py-4 pr-6 text-left font-mono text-[11px] uppercase tracking-wider">
                      {t('compare.feature')}
                    </th>
                    <th className="py-4 px-4 text-center font-semibold">Evershade</th>
                    <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">Cursor</th>
                    <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">Copilot</th>
                    <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">Aider</th>
                    <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">OpenDevin</th>
                  </tr>
                </thead>
                <tbody>
                  {category.features.map((row) => (
                    <tr key={row.feature} className="border-b border-border">
                      <td className="py-3 pr-6 font-medium">{row.feature}</td>
                      <td className="py-3 px-4 text-center">
                        <Check className="mx-auto size-4 text-signal" aria-hidden="true" />
                      </td>
                      <td className="py-3 px-4 text-center">
                        {row.cursor ? (
                          <Check className="mx-auto size-4 text-muted-foreground" aria-hidden="true" />
                        ) : (
                          <X className="mx-auto size-4 text-muted-foreground/40" aria-hidden="true" />
                        )}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {row.copilot ? (
                          <Check className="mx-auto size-4 text-muted-foreground" aria-hidden="true" />
                        ) : (
                          <X className="mx-auto size-4 text-muted-foreground/40" aria-hidden="true" />
                        )}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {row.aider ? (
                          <Check className="mx-auto size-4 text-muted-foreground" aria-hidden="true" />
                        ) : (
                          <X className="mx-auto size-4 text-muted-foreground/40" aria-hidden="true" />
                        )}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {row.opendevin ? (
                          <Check className="mx-auto size-4 text-muted-foreground" aria-hidden="true" />
                        ) : (
                          <X className="mx-auto size-4 text-muted-foreground/40" aria-hidden="true" />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>

      {/* Why cards */}
      <div className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-20">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">
          {t('compare.why-title')}
        </p>
        <div className="mt-6 stagger grid gap-6 md:mt-8 md:grid-cols-2">
          {WHY_CARDS.map((card) => (
            <div key={card.title} className="border-t border-foreground pt-6">
              <h3 className="text-xl font-semibold tracking-tight md:text-2xl">{card.title}</h3>
              <p className="mt-3 text-pretty leading-snug text-muted-foreground">{card.body}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="mx-4 mt-16 border border-border p-8 text-center md:mx-[max(24px,3vw)] md:mt-20">
        <h2 className="text-2xl font-semibold tracking-tight md:text-3xl">
          {t('compare.cta-title')}<span className="text-signal">.</span>
        </h2>
        <p className="mt-3 text-muted-foreground">{t('compare.cta-description')}</p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <a
            href="/"
            className="inline-flex items-center gap-1.5 rounded-sm border border-foreground px-4 py-2 text-sm font-medium transition-colors hover:bg-foreground hover:text-background"
          >
            {t('compare.cta-button')}
          </a>
          <a
            href="https://github.com/LukaG712/Evershade"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 rounded-sm border border-border px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:border-foreground/20 hover:text-foreground"
          >
            {t('compare.cta-github')}
          </a>
        </div>
      </div>

      {/* Spacer for mobile TOC */}
      <div className="h-20" />
    </div>
  )
}
