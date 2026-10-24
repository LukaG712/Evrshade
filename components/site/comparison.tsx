import { Check, X } from 'lucide-react'
import { SectionHeading } from './section-heading'

const COMPARISON = [
  { feature: 'Self-hosted', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
  { feature: 'Modular microservices', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
  { feature: 'No cloud dependency', evershade: true, cursor: false, copilot: false, aider: true, opendevin: true },
  { feature: 'Approval gates', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
  { feature: 'Knowledge graph memory', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
  { feature: 'Sandboxed execution', evershade: true, cursor: false, copilot: false, aider: false, opendevin: true },
  { feature: 'Web dashboard', evershade: true, cursor: true, copilot: false, aider: false, opendevin: true },
  { feature: 'CLI interface', evershade: true, cursor: false, copilot: false, aider: true, opendevin: false },
  { feature: 'Runs on dev hardware', evershade: true, cursor: true, copilot: true, aider: true, opendevin: true },
  { feature: 'Secrets encryption', evershade: true, cursor: false, copilot: false, aider: false, opendevin: false },
] as const

const WHY_POINTS = [
  {
    title: 'You own everything',
    body: 'Your code, your data, your secrets - all stored locally. No cloud vendor, no telemetry, no surprise API bills.',
  },
  {
    title: 'Modular by design',
    body: '10 independent services you can mix and match. Run just the core, or add observability, notifications, and a web dashboard.',
  },
  {
    title: 'Built for trust',
    body: 'Approval gates, sandboxed execution, encrypted secrets, and prompt injection defense - security is the default, not an afterthought.',
  },
  {
    title: 'Lightweight infra',
    body: 'SQLite, Docker Compose, and ordinary developer hardware. No Kubernetes, Kafka, or Elasticsearch required.',
  },
] as const

export function Comparison() {
  return (
    <section id="why" aria-labelledby="why-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="why-title"
        label="Why Evershade"
        title={
          <>
            Built different<span className="text-signal">.</span>
            <br />
            <span className="text-muted-foreground">Built for you.</span>
          </>
        }
        lead="Evershade is a self-hosted AI agent platform where you control the infrastructure, the data, and the autonomy. Here's how it compares to the alternatives."
      />

      <div className="mt-12 stagger grid gap-6 md:mt-16 md:grid-cols-2">
        {WHY_POINTS.map((point) => (
          <div key={point.title} className="border-t border-foreground pt-6">
            <h3 className="text-2xl font-semibold tracking-tight md:text-3xl">{point.title}</h3>
            <p className="mt-3 text-pretty leading-snug text-muted-foreground">{point.body}</p>
          </div>
        ))}
      </div>

      {/* Mobile: simplified comparison */}
      <div className="mt-12 md:hidden">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Feature comparison'}</p>
        <div className="mt-6 space-y-3">
          {[
            { name: 'Cursor', count: COMPARISON.filter(r => r.cursor).length },
            { name: 'Copilot', count: COMPARISON.filter(r => r.copilot).length },
            { name: 'Aider', count: COMPARISON.filter(r => r.aider).length },
            { name: 'OpenDevin', count: COMPARISON.filter(r => r.opendevin).length },
          ].map((competitor) => (
            <div key={competitor.name} className="flex items-center justify-between border border-border p-3">
              <p className="font-medium text-sm">{competitor.name}</p>
              <span className="font-mono text-xs text-muted-foreground">{competitor.count}/{COMPARISON.length}</span>
            </div>
          ))}
          <div className="flex items-center justify-between border border-signal bg-signal/5 p-3">
            <p className="font-semibold text-sm text-signal-ink">Evershade</p>
            <span className="font-mono text-xs text-signal-ink">{COMPARISON.length}/{COMPARISON.length}</span>
          </div>
        </div>
      </div>

      {/* Desktop: full comparison table */}
      <div className="hidden mt-16 md:block md:mt-32">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'14.1: Feature comparison'}</p>
        <div className="mt-6 overflow-x-auto border-t border-foreground">
          <table className="w-full min-w-[640px] text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="py-4 pr-6 text-left font-mono text-[11px] uppercase tracking-wider">Feature</th>
                <th className="py-4 px-4 text-center font-semibold">Evershade</th>
                <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">Cursor</th>
                <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">Copilot</th>
                <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">Aider</th>
                <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">OpenDevin</th>
              </tr>
            </thead>
            <tbody>
              {COMPARISON.map((row) => (
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
        <p className="mt-3 font-mono text-[10px] text-muted-foreground">{'Based on public documentation as of October 2026. Features may change.'}</p>
      </div>
    </section>
  )
}
