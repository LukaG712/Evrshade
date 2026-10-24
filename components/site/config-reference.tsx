import { Key, Settings } from 'lucide-react'
import { SectionHeading } from './section-heading'

const ENV_VARS = [
  {
    category: 'Required',
    vars: [
      { name: 'OPENAI_API_KEY', desc: 'API key for OpenAI models (gpt-4o, etc.)' },
      { name: 'ANTHROPIC_API_KEY', desc: 'API key for Anthropic models (Claude)' },
      { name: 'GOOGLE_API_KEY', desc: 'API key for Google models (Gemini)' },
    ],
  },
  {
    category: 'Optional',
    vars: [
      { name: 'OLLAMA_HOST', desc: 'Ollama server address for local models (default: http://localhost:11434)' },
      { name: 'SLACK_WEBHOOK_URL', desc: 'Incoming webhook URL for Slack notifications' },
      { name: 'DISCORD_WEBHOOK_URL', desc: 'Incoming webhook URL for Discord notifications' },
      { name: 'TELEGRAM_BOT_TOKEN', desc: 'Bot token for Telegram notifications' },
      { name: 'TELEGRAM_CHAT_ID', desc: 'Chat ID for Telegram notifications' },
      { name: 'SMTP_HOST', desc: 'SMTP server for email notifications' },
      { name: 'SMTP_PORT', desc: 'SMTP port (default: 587)' },
      { name: 'SMTP_USER', desc: 'SMTP username' },
      { name: 'SMTP_PASSWORD', desc: 'SMTP password' },
      { name: 'GITHUB_TOKEN', desc: 'Token for GitHub webhook authentication' },
    ],
  },
  {
    category: 'Advanced',
    vars: [
      { name: 'AUTONOMY_LEVEL', desc: 'Default autonomy: supervised, restricted, or full (default: restricted)' },
      { name: 'MAX_WORKERS', desc: 'Maximum parallel workers per milestone (default: 4)' },
      { name: 'MAX_FIX_RETRIES', desc: 'Max fix-revalidate loop iterations (default: 3)' },
      { name: 'LOG_LEVEL', desc: 'Log verbosity: debug, info, warn, error (default: info)' },
    ],
  },
] as const

export function ConfigReference() {
  return (
    <section id="config-reference" aria-labelledby="config-reference-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="config-reference-title"
        label="Config"
        title={
          <>
            Environment
            <span className="text-signal"> variables.</span>
          </>
        }
        lead="Copy .env.example to .env and fill in the values you need. Only model API keys are required to get started."
      />

      <div className="mt-12 space-y-8 md:mt-24">
        {ENV_VARS.map((group) => (
          <div key={group.category}>
            <div className="flex items-center gap-2">
              {group.category === 'Required' ? (
                <Key className="size-4 text-signal-ink" aria-hidden="true" />
              ) : (
                <Settings className="size-4 text-muted-foreground" aria-hidden="true" />
              )}
              <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{group.category}</p>
            </div>
            <div className="mt-4 overflow-hidden border border-border sm:overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-card">
                    <th className="px-3 py-2.5 text-left font-mono text-[10px] uppercase tracking-wider text-muted-foreground sm:px-4 sm:py-3">
                      Variable
                    </th>
                    <th className="px-3 py-2.5 text-left font-mono text-[10px] uppercase tracking-wider text-muted-foreground sm:px-4 sm:py-3">
                      Description
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {group.vars.map((v, i) => (
                    <tr key={v.name} className={i < group.vars.length - 1 ? 'border-b border-border' : ''}>
                      <td className="px-3 py-2.5 font-mono text-xs font-semibold sm:px-4 sm:py-3">{v.name}</td>
                      <td className="px-3 py-2.5 text-muted-foreground sm:px-4 sm:py-3">{v.desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-12 rounded border border-border bg-card p-5">
        <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Tip</p>
        <p className="mt-2 text-sm leading-snug text-muted-foreground">
          For local development with Ollama, you don't need any cloud API keys. Set <code className="font-mono text-xs">OLLAMA_HOST</code> and use local models for near-zero cost.
        </p>
      </div>
    </section>
  )
}
