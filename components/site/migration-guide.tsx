import { Check, X } from 'lucide-react'
import { SectionHeading } from './section-heading'

const PLATFORMS = [
  {
    name: 'Cursor',
    tagline: 'AI-powered code editor',
    painPoints: [
      'Cloud-dependent — your code leaves your machine',
      'No modular architecture — all-or-nothing',
      'No approval gates for autonomous actions',
      'No persistent memory across sessions',
    ],
    evershadeFix: [
      'Fully self-hosted — code never leaves your network',
      '10 independent services you mix and match',
      'Three autonomy levels with human-in-the-loop approval',
      'Gobber knowledge graph remembers everything',
    ],
    switchEase: 'Complementary — use Evershade for agent workflows alongside Cursor for editing',
  },
  {
    name: 'GitHub Copilot',
    tagline: 'Cloud AI assistant',
    painPoints: [
      'Subscription cost per user, per month',
      'No local autonomy — just inline suggestions',
      'No sandboxed execution or secrets management',
      'No observability or mission tracking',
    ],
    evershadeFix: [
      'MIT licensed — run it forever, no subscription',
      'Full autonomous agents with mission lifecycle',
      'Hider for encrypted secrets, Slinker for sandboxed execution',
      'Sneaker for metrics, traces, and logs',
    ],
    switchEase: 'Drop-in replacement for autonomous tasks — keep Copilot for inline suggestions if you want',
  },
  {
    name: 'Aider',
    tagline: 'AI pair programming in terminal',
    painPoints: [
      'Single-process — no microservices or parallel workers',
      'No web dashboard for monitoring',
      'No knowledge graph or persistent memory',
      'No notification system for async updates',
    ],
    evershadeFix: [
      'Parallel workers across milestones and features',
      'Slammer React dashboard with live SSE streaming',
      'Gobber stores and retrieves knowledge across sessions',
      'Poltergeist delivers Slack, Discord, email, and Telegram alerts',
    ],
    switchEase: 'Similar CLI workflow — Speedy CLI mirrors Aider\'s terminal experience with more services',
  },
  {
    name: 'OpenDevin',
    tagline: 'Open-source AI agent',
    painPoints: [
      'Monolithic — hard to customize or extend parts',
      'No secrets encryption or approval gates',
      'Limited observability — no traces or metrics',
      'No plugin ecosystem for custom tools',
    ],
    evershadeFix: [
      'Modular by design — swap services without touching the rest',
      'Hider for secrets, Greenie for approval gates',
      'Sneaker provides full OpenTelemetry-compatible observability',
      'Harness plugin registry for custom skills and tools',
    ],
    switchEase: 'Direct replacement — same self-hosted model, more modular and more secure',
  },
] as const

const COMPARISON_ROWS = [
  { feature: 'Self-hosted', cursor: false, copilot: false, aider: true, opendevin: true },
  { feature: 'No subscription fee', cursor: false, copilot: false, aider: true, opendevin: true },
  { feature: 'Modular services', cursor: false, copilot: false, aider: false, opendevin: false },
  { feature: 'Approval gates', cursor: false, copilot: false, aider: false, opendevin: false },
  { feature: 'Knowledge graph', cursor: false, copilot: false, aider: false, opendevin: false },
  { feature: 'Encrypted secrets', cursor: false, copilot: false, aider: false, opendevin: false },
  { feature: 'Web dashboard', cursor: true, copilot: false, aider: false, opendevin: true },
  { feature: 'CLI interface', cursor: false, copilot: false, aider: true, opendevin: false },
  { feature: 'Observability', cursor: false, copilot: false, aider: false, opendevin: false },
  { feature: 'Notifications', cursor: false, copilot: false, aider: false, opendevin: false },
  { feature: 'Plugin ecosystem', cursor: false, copilot: false, aider: false, opendevin: false },
  { feature: 'Parallel workers', cursor: false, copilot: false, aider: false, opendevin: false },
] as const

export function MigrationGuide() {
  return (
    <section id="migration" aria-labelledby="migration-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="migration-title"
        label="Migration guide"
        title={<>Why switch<span className="text-signal">.</span></>}
        lead="Coming from another AI platform? Here's what you gain by switching to Evershade, and how easy the migration is."
      />

      {/* Platform cards */}
      <div className="mt-12 stagger space-y-4 md:mt-16">
        {PLATFORMS.map((platform) => (
          <div
            key={platform.name}
            className="border border-border p-6"
          >
            <div className="flex flex-col gap-4 md:flex-row md:items-start">
              <div className="md:w-48 shrink-0">
                <h3 className="text-lg font-semibold tracking-tight">{platform.name}</h3>
                <p className="mt-0.5 text-sm text-muted-foreground">{platform.tagline}</p>
                <div className="mt-3 rounded border border-foreground/40 px-2.5 py-1.5">
                  <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Switch effort</p>
                  <p className="mt-1 text-xs leading-snug">{platform.switchEase}</p>
                </div>
              </div>
              <div className="flex-1 grid gap-4 md:grid-cols-2">
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">The pain points</p>
                  <ul className="mt-2 space-y-1.5">
                    {platform.painPoints.map((point) => (
                      <li key={point} className="flex items-start gap-2 text-sm">
                        <X className="mt-0.5 size-4 shrink-0 text-muted-foreground/40" aria-hidden="true" />
                        <span className="text-muted-foreground">{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-wider text-signal-ink">Evershade fixes it</p>
                  <ul className="mt-2 space-y-1.5">
                    {platform.evershadeFix.map((fix) => (
                      <li key={fix} className="flex items-start gap-2 text-sm">
                        <Check className="mt-0.5 size-4 shrink-0 text-signal" aria-hidden="true" />
                        <span>{fix}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary comparison table */}
      <div className="mt-16 md:mt-24">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Feature summary'}</p>
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
              {COMPARISON_ROWS.map((row) => (
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
