import Link from 'next/link'
import { Check, X } from 'lucide-react'
import { SectionHeading } from '@/components/site/section-heading'

const CATEGORIES = [
  {
    name: 'Core',
    features: [
      ['Self-hosted', true, true, true, true],
      ['Modular microservices', true, false, false, false],
      ['10 independent services', true, false, false, false],
      ['Docker Compose only', true, false, false, true],
      ['No external dependencies', true, false, false, false],
    ],
  },
  {
    name: 'Security',
    features: [
      ['Approval gates', true, false, false, false],
      ['Autonomy dial', true, false, false, false],
      ['Encrypted secrets (AES-256)', true, false, false, false],
      ['Container isolation', true, false, false, true],
      ['Prompt injection defenses', true, false, false, false],
    ],
  },
  {
    name: 'Memory & Knowledge',
    features: [
      ['Knowledge graph', true, false, false, false],
      ['Persistent memory', true, false, false, false],
      ['Vector embeddings', true, false, false, false],
      ['Keyword search', true, false, false, false],
    ],
  },
  {
    name: 'Observability',
    features: [
      ['Built-in metrics', true, false, false, false],
      ['Distributed traces', true, false, false, false],
      ['Structured logs', true, false, false, false],
      ['Real-time streaming', true, false, false, false],
    ],
  },
  {
    name: 'Architecture',
    features: [
      ['SQLite-first', true, false, false, false],
      ['HTTP REST APIs', true, false, false, false],
      ['No message queues', true, false, false, false],
      ['Graceful degradation', true, false, false, false],
    ],
  },
  {
    name: 'Models & Providers',
    features: [
      ['OpenAI compatible', true, true, true, true],
      ['Anthropic', true, true, true, true],
      ['Ollama (local)', true, false, true, false],
      ['Provider abstraction', true, false, false, false],
    ],
  },
  {
    name: 'Cost',
    features: [
      ['Free (MIT)', true, false, true, true],
      ['No credits', true, false, true, true],
      ['No rate limits', true, false, true, true],
      ['No vendor lock-in', true, false, true, true],
    ],
  },
]

const PLATFORMS = ['Evershade', 'Cursor', 'Copilot', 'OpenDevin']

export default function ComparePage() {
  return (
    <div className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="compare-title"
        label="Compare"
        title={
          <>
            Side by side,
            <br />
            <span className="text-muted-foreground">clearly.</span>
          </>
        }
        lead="39 features across 7 categories. Evershade vs the alternatives."
      />

      {/* Summary */}
      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {CATEGORIES.reduce((acc, cat) => {
          const score = cat.features.filter((f) => f[1]).length
          acc.push({ name: cat.name, score, total: cat.features.length })
          return acc
        }, [] as { name: string; score: number; total: number }[]).map((item) => (
          <div key={item.name} className="border border-foreground p-5">
            <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{item.name}</p>
            <p className="mt-2 text-3xl font-semibold tracking-tight">
              {item.score}<span className="text-muted-foreground">/{item.total}</span>
            </p>
          </div>
        ))}
      </div>

      {/* Categories */}
      {CATEGORIES.map((cat) => (
        <div key={cat.name} className="mt-16">
          <h2 className="text-2xl font-semibold tracking-tight">{cat.name}</h2>
          <div className="mt-6 overflow-x-auto border-t border-foreground">
            <table className="w-full min-w-[600px] text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="py-4 pr-6 text-left font-medium">Feature</th>
                  {PLATFORMS.map((p) => (
                    <th key={p} className={`py-4 px-4 text-center font-mono text-[11px] ${p === 'Evershade' ? 'font-semibold' : 'text-muted-foreground'}`}>
                      {p}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {cat.features.map((row) => (
                  <tr key={row[0] as string} className="border-b border-border">
                    <td className="py-3 pr-6 font-medium">{row[0]}</td>
                    {row.slice(1).map((val, i) => (
                      <td key={i} className="py-3 px-4 text-center">
                        {val ? (
                          <Check className={`mx-auto size-4 ${i === 0 ? 'text-signal' : 'text-muted-foreground'}`} />
                        ) : (
                          <X className="mx-auto size-4 text-muted-foreground/40" />
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}

      {/* Why it matters */}
      <div className="mt-16 grid gap-4 sm:grid-cols-2">
        {[
          { title: 'Security', desc: 'Approval gates and container isolation keep you in control. No other platform offers this level of human-in-the-loop security.' },
          { title: 'Observability', desc: 'Built-in metrics, traces, and logs mean you can debug AI agents without setting up separate infrastructure.' },
          { title: 'Modularity', desc: '10 independent services mean you can swap, extend, or disable any piece without breaking the whole platform.' },
          { title: 'Data', desc: 'Knowledge graph with persistent memory means your agents learn from every session. No amnesia.' },
        ].map((item) => (
          <div key={item.title} className="border border-foreground p-5">
            <p className="font-semibold tracking-tight">{item.title}</p>
            <p className="mt-2 text-sm leading-snug text-muted-foreground">{item.desc}</p>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div className="mt-16 border-t border-foreground pt-8 text-center">
        <p className="text-lg font-semibold tracking-tight">Ready to try Evershade?</p>
        <div className="mt-4 flex items-center justify-center gap-4">
          <Link href="/" className="inline-flex h-11 items-center gap-2 border border-foreground px-5 text-sm font-medium transition-colors hover:bg-foreground hover:text-background">
            Back to home
          </Link>
          <a
            href="https://github.com/LukaG712/Evershade"
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-11 items-center gap-2 bg-foreground px-5 text-sm font-medium text-background transition-colors hover:bg-signal-ink"
          >
            View on GitHub
          </a>
        </div>
      </div>
    </div>
  )
}
