import { SectionHeading } from './section-heading'

const VARS = [
  { var: 'DATABASE_URL', default: 'sqlite:///data/greenie.db', desc: 'SQLite connection string for Greenie' },
  { var: 'LLM_PROVIDER', default: 'openai', desc: 'LLM provider: openai, anthropic, ollama' },
  { var: 'LLM_API_KEY', default: '', desc: 'API key for the LLM provider' },
  { var: 'LLM_MODEL', default: 'gpt-4o', desc: 'Default model for LLM calls' },
  { var: 'AUTONOMY_LEVEL', default: 'partial', desc: 'Agent autonomy: full, partial, none' },
  { var: 'SECRET_KEY', default: '(auto-generated)', desc: 'Master key for Hider encryption' },
  { var: 'REDIS_URL', default: 'redis://localhost:6379', desc: 'Redis connection for Trapper' },
  { var: 'SLAMMER_PORT', default: '5173', desc: 'Port for the Slammer web dashboard' },
]

export function ConfigReference() {
  return (
    <section id="config-reference" aria-labelledby="config-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="config-title"
        label="Config reference"
        title={
          <>
            Environment variables,
            <br />
            <span className="text-muted-foreground">documented.</span>
          </>
        }
        lead="Copy .env.example to .env and set the variables you need. Everything else uses sensible defaults."
      />

      <div className="mt-16 overflow-x-auto border-t border-foreground">
        <table className="w-full min-w-[600px] text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="py-4 pr-6 text-left font-mono text-[11px] uppercase tracking-wider">Variable</th>
              <th className="py-4 px-4 text-left font-mono text-[11px] uppercase tracking-wider">Default</th>
              <th className="py-4 px-4 text-left font-mono text-[11px] uppercase tracking-wider">Description</th>
            </tr>
          </thead>
          <tbody>
            {VARS.map((v) => (
              <tr key={v.var} className="border-b border-border">
                <td className="py-3 pr-6 font-mono text-sm font-semibold">{v.var}</td>
                <td className="py-3 px-4 font-mono text-xs text-muted-foreground">{v.default || '(required)'}</td>
                <td className="py-3 px-4 text-muted-foreground">{v.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
