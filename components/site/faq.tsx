'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { SectionHeading } from './section-heading'

const FAQ = [
  {
    q: 'Do I need a GPU?',
    a: 'No. Evershade runs on ordinary developer hardware. LLM calls happen over the network through Shrewd, so no local GPU is required.',
  },
  {
    q: 'Can I run just some services?',
    a: 'Yes. Use profiles (minimal, standard, full, custom) to pick exactly which services you need. The minimal profile runs just the 4 core services.',
  },
  {
    q: 'Is my data safe?',
    a: 'Everything stays on your machine. No telemetry, no cloud dependency. Secrets are encrypted with AES-256-GCM at rest in Hider.',
  },
  {
    q: 'Which LLM providers are supported?',
    a: 'Any provider with an OpenAI-compatible API. Shrewd abstracts the provider layer, so you can swap between OpenAI, Anthropic, Ollama, or any other provider.',
  },
  {
    q: 'Can I use local models?',
    a: 'Yes. With the Ollama profile, you can run models entirely on your machine with no external API calls.',
  },
  {
    q: 'How do I update?',
    a: 'Pull the latest changes from each service repo and restart with ./start.sh. The CLI handles version compatibility checks.',
  },
  {
    q: 'Is there a web UI?',
    a: 'Yes. Slammer is the React web dashboard. Monitor missions, approve operations, watch agents work, and review logs in real time.',
  },
  {
    q: 'What about backups?',
    a: 'All data is stored in SQLite databases. Back up the data directory and you have a complete snapshot of your Evershade instance.',
  },
]

export function Faq() {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <section id="faq" aria-labelledby="faq-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="faq-title"
        label="FAQ"
        title={
          <>
            Common questions,
            <br />
            <span className="text-muted-foreground">answered.</span>
          </>
        }
      />

      <div className="mt-16 max-w-3xl">
        {FAQ.map((item, i) => (
          <div key={item.q} className="border-b border-border">
            <button
              type="button"
              onClick={() => setOpen(open === i ? null : i)}
              className="flex w-full items-center justify-between py-5 text-left font-semibold tracking-tight"
              aria-expanded={open === i}
            >
              {item.q}
              <ChevronDown
                className={cn(
                  'size-4 shrink-0 text-muted-foreground transition-transform',
                  open === i && 'rotate-180',
                )}
                aria-hidden="true"
              />
            </button>
            {open === i && (
              <p className="pb-5 text-sm leading-snug text-muted-foreground">{item.a}</p>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
