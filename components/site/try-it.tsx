'use client'

import { Check, Copy } from 'lucide-react'
import { useState } from 'react'
import { SectionHeading } from './section-heading'

const COMMANDS = [
  { comment: '# clone', cmd: 'git clone https://github.com/LukaG712/Evershade.git && cd Evershade' },
  { comment: '# install', cmd: './install.sh --profile minimal' },
  { comment: '# configure', cmd: 'cp .env.example .env' },
  { comment: '# start', cmd: './start.sh --profile minimal' },
]

export function TryIt() {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    await navigator.clipboard.writeText(COMMANDS.map((c) => c.cmd).join('\n'))
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }

  return (
    <section id="try-it" aria-labelledby="try-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="try-title"
        label="Try it"
        title={
          <>
            Start in under,
            <br />
            <span className="text-muted-foreground">a minute.</span>
          </>
        }
        lead="Four commands. That's all it takes to get Evershade running on your machine."
      />

      <div className="mt-16 max-w-2xl border border-foreground">
        <div className="flex items-center justify-between border-b border-foreground px-4 py-2.5">
          <span className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">Terminal</span>
          <button
            type="button"
            onClick={copy}
            className="inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-wider transition-colors hover:text-signal-ink"
          >
            {copied ? <Check className="size-3.5 text-signal-ink" /> : <Copy className="size-3.5" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
        <pre className="overflow-x-auto p-5 font-mono text-[13px] leading-relaxed md:p-6">
          <code>
            {COMMANDS.map((c) => (
              <span key={c.cmd} className="block">
                <span className="text-muted-foreground">{c.comment}</span>
                {'\n'}
                <span className="text-signal-ink">{'$ '}</span>
                {c.cmd}
                {'\n\n'}
              </span>
            ))}
          </code>
        </pre>
      </div>
    </section>
  )
}
