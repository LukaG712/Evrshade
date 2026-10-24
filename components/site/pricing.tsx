'use client'

import { Check, X } from 'lucide-react'
import { SectionHeading } from './section-heading'
import { useI18n } from '@/lib/i18n'

const COST_COMPARISON = [
  { name: 'Cursor', price: '$20', period: '/mo', note: 'Pro plan' },
  { name: 'GitHub Copilot', price: '$19', period: '/mo', note: 'Business plan' },
  { name: 'Aider', price: '$0–$50', period: '/mo', note: 'API costs vary' },
  { name: 'OpenDevin', price: '$0–$100', period: '/mo', note: 'Cloud/infra costs' },
  { name: 'Evershade', price: '$0', period: '', note: 'Forever, MIT' },
] as const

const WHAT_YOU_GET = [
  { title: '10 microservices', description: 'Greenie, Slinker, Trapper, Gobber, Shrewd, Sneaker, Hider, Poltergeist, Slammer, Speedy — all included.' },
  { title: 'Full observability', description: 'Metrics, traces, and logs built in. No extra tools or subscriptions needed.' },
  { title: 'Knowledge graph memory', description: 'Persistent agent memory with semantic search. Your agents learn and remember.' },
  { title: 'Approval gates', description: 'Human-in-the-loop controls. Nothing runs without your say-so.' },
  { title: 'Encrypted secrets', description: 'AES-256 encryption for all API keys and credentials. Stored locally.' },
  { title: 'Web dashboard', description: 'Slammer provides a full browser-based control panel. No CLI required.' },
] as const

const WHAT_YOU_PAY = [
  { item: 'Docker Desktop', cost: 'Free', note: 'For personal use' },
  { item: 'Your hardware', cost: 'Already owned', note: 'Runs on dev machines' },
  { item: 'LLM API calls', cost: 'Pay-per-use', note: 'You choose your provider' },
  { item: 'Domain (optional)', cost: '~$10/yr', note: 'Only if you want a custom URL' },
  { item: 'Your time', cost: '~5 min', note: 'To get up and running' },
] as const

export function Pricing() {
  const { t } = useI18n()
  return (
    <section id="pricing" aria-labelledby="pricing-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="pricing-title"
        label="Pricing"
        title={
          <>
            Free<span className="text-signal">.</span>
            <br />
            <span className="text-muted-foreground">Forever.</span>
          </>
        }
        lead="Evershade is open-source software under the MIT license. No tiers, no credits, no surprise bills. Here's what that actually means."
      />

      {/* The big zero */}
      <div className="mt-12 border border-border p-8 text-center md:mt-16">
        <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{t('pricing.total-cost')}</p>
        <p className="mt-4 text-8xl font-semibold tracking-tight text-foreground md:text-9xl">$0</p>
        <p className="mt-2 text-lg text-muted-foreground">{t('pricing.total-cost-note')}</p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <span className="inline-flex items-center gap-1.5 rounded-sm border border-border px-3 py-1 font-mono text-xs text-muted-foreground">
            <Check className="size-3 text-signal" /> MIT License
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-sm border border-border px-3 py-1 font-mono text-xs text-muted-foreground">
            <Check className="size-3 text-signal" /> Self-hosted
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-sm border border-border px-3 py-1 font-mono text-xs text-muted-foreground">
            <Check className="size-3 text-signal" /> No telemetry
          </span>
        </div>
      </div>

      {/* Cost comparison */}
      <div className="mt-16 md:mt-20">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{t('pricing.comparison-title')}</p>
        <div className="mt-6 grid gap-4 md:grid-cols-5">
          {COST_COMPARISON.map((item) => (
            <div
              key={item.name}
              className={`rounded-sm border p-5 text-center transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${
                item.name === 'Evershade'
                  ? 'border-signal bg-signal/5'
                  : 'border-border'
              }`}
            >
              <p className={`text-sm font-medium ${item.name === 'Evershade' ? 'text-signal-ink' : 'text-muted-foreground'}`}>
                {item.name}
              </p>
              <p className={`mt-3 text-3xl font-semibold tracking-tight ${item.name === 'Evershade' ? 'text-signal-ink' : ''}`}>
                {item.price}
                <span className="text-sm font-normal text-muted-foreground">{item.period}</span>
              </p>
              <p className="mt-2 font-mono text-[10px] text-muted-foreground">{item.note}</p>
            </div>
          ))}
        </div>
      </div>

      {/* What you get */}
      <div className="mt-16 md:mt-20">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{t('pricing.what-you-get')}</p>
        <div className="mt-6 stagger grid gap-6 md:mt-8 md:grid-cols-2">
          {WHAT_YOU_GET.map((item) => (
            <div key={item.title} className="border-t border-foreground pt-6">
              <h3 className="text-xl font-semibold tracking-tight md:text-2xl">{item.title}</h3>
              <p className="mt-2 text-pretty leading-snug text-muted-foreground">{item.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* What you actually pay */}
      <div className="mt-16 md:mt-20">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{t('pricing.real-costs')}</p>
        <div className="mt-6 overflow-x-auto border-t border-foreground md:mt-8">
          <table className="w-full min-w-[480px] text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="py-4 pr-6 text-left font-mono text-[11px] uppercase tracking-wider">{t('pricing.item')}</th>
                <th className="py-4 px-4 text-left font-mono text-[11px] uppercase tracking-wider">{t('pricing.cost')}</th>
                <th className="py-4 pl-4 text-left font-mono text-[11px] uppercase tracking-wider">{t('pricing.note')}</th>
              </tr>
            </thead>
            <tbody>
              {WHAT_YOU_PAY.map((item) => (
                <tr key={item.item} className="border-b border-border">
                  <td className="py-3 pr-6 font-medium">{item.item}</td>
                  <td className="py-3 px-4">{item.cost}</td>
                  <td className="py-3 pl-4 text-muted-foreground">{item.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Future cloud tier teaser */}
      <div className="mt-16 border border-dashed border-border p-8 md:mt-20">
        <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{t('pricing.future-title')}</p>
        <h3 className="mt-4 text-2xl font-semibold tracking-tight md:text-3xl">{t('pricing.future-heading')}</h3>
        <p className="mt-3 max-w-2xl text-pretty leading-snug text-muted-foreground">
          {t('pricing.future-description')}
        </p>
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <span className="inline-flex items-center gap-1.5 rounded-sm border border-border px-3 py-1 font-mono text-xs text-muted-foreground">
            <X className="size-3 text-muted-foreground/40" /> {t('pricing.no-credits')}
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-sm border border-border px-3 py-1 font-mono text-xs text-muted-foreground">
            <X className="size-3 text-muted-foreground/40" /> {t('pricing.no-rate-limits')}
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-sm border border-border px-3 py-1 font-mono text-xs text-muted-foreground">
            <X className="size-3 text-muted-foreground/40" /> {t('pricing.no-vendor-lock')}
          </span>
        </div>
      </div>
    </section>
  )
}
