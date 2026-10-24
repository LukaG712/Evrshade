import { Check, X } from 'lucide-react'
import { SectionHeading } from './section-heading'

const PLATFORMS = [
  {
    name: 'Cursor',
    pain: 'Cloud-dependent, no modular services, no approval gates',
    fix: 'Self-hosted, 10 microservices, human-in-the-loop approval',
  },
  {
    name: 'GitHub Copilot',
    pain: 'Single-service, no mission workflow, no observability',
    fix: 'Mission-based workflow, built-in metrics, traces, and logs',
  },
  {
    name: 'Aider',
    pain: 'CLI-only, no knowledge graph, no secrets management',
    fix: 'Web dashboard, persistent knowledge graph, encrypted secrets',
  },
  {
    name: 'OpenDevin',
    pain: 'Heavy infrastructure, no approval gates, no sandboxing',
    fix: 'Docker Compose only, approval gates, container isolation',
  },
]

const FEATURES = [
  ['Self-hosted', true, true, true, true],
  ['Modular microservices', true, false, false, false],
  ['Approval gates', true, false, false, false],
  ['Knowledge graph', true, false, false, false],
  ['Encrypted secrets', true, false, false, false],
  ['Built-in observability', true, false, false, false],
  ['Web dashboard', true, false, false, true],
  ['SQLite-first', true, false, false, false],
]

export function MigrationGuide() {
  return (
    <section id="migration" aria-labelledby="migration-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="migration-title"
        label="Why switch"
        title={
          <>
            Coming from,
            <br />
            <span className="text-muted-foreground">something else?</span>
          </>
        }
        lead="Evershade combines the best of self-hosted AI platforms while adding capabilities others lack."
      />

      <div className="mt-16 grid gap-4 md:grid-cols-2">
        {PLATFORMS.map((p) => (
          <div key={p.name} className="border border-foreground p-5">
            <p className="text-lg font-semibold tracking-tight">{p.name}</p>
            <div className="mt-3 space-y-2">
              <p className="flex items-start gap-2 text-sm text-muted-foreground">
                <X className="mt-0.5 size-4 shrink-0 text-muted-foreground/40" aria-hidden="true" />
                {p.pain}
              </p>
              <p className="flex items-start gap-2 text-sm">
                <Check className="mt-0.5 size-4 shrink-0 text-signal" aria-hidden="true" />
                {p.fix}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-16 overflow-x-auto border-t border-foreground">
        <table className="w-full min-w-[600px] text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="py-4 pr-6 text-left font-mono text-[11px] uppercase tracking-wider">Feature</th>
              <th className="py-4 px-4 text-center font-semibold">Evershade</th>
              <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">Cursor</th>
              <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">Copilot</th>
              <th className="py-4 px-4 text-center font-mono text-[11px] text-muted-foreground">OpenDevin</th>
            </tr>
          </thead>
          <tbody>
            {FEATURES.map((row) => (
              <tr key={row[0] as string} className="border-b border-border">
                <td className="py-3 pr-6 font-medium">{row[0]}</td>
                <td className="py-3 px-4 text-center"><Check className="mx-auto size-4 text-signal" /></td>
                <td className="py-3 px-4 text-center">
                  {row[2] ? <Check className="mx-auto size-4 text-muted-foreground" /> : <X className="mx-auto size-4 text-muted-foreground/40" />}
                </td>
                <td className="py-3 px-4 text-center">
                  {row[3] ? <Check className="mx-auto size-4 text-muted-foreground" /> : <X className="mx-auto size-4 text-muted-foreground/40" />}
                </td>
                <td className="py-3 px-4 text-center">
                  {row[4] ? <Check className="mx-auto size-4 text-muted-foreground" /> : <X className="mx-auto size-4 text-muted-foreground/40" />}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
