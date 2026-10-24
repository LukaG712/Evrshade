'use client'

import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react'
import { useState } from 'react'
import { SectionHeading } from './section-heading'

const FAQ = [
  {
    q: 'Do I need a GPU?',
    a: 'No. Evershade runs entirely on CPU. If you use cloud models (OpenAI, Anthropic, Google), all heavy lifting happens on their servers. Local models via Ollama also run on CPU, though they will be slower.',
  },
  {
    q: 'Can I use my own API key?',
    a: 'Yes. Evershade is designed to be self-hosted. You provide your own API keys for the models you want to use. Your data never leaves your machine except for the model API calls you explicitly make.',
  },
  {
    q: 'How much disk space does it need?',
    a: 'The minimal profile (4 core services) uses approximately 500MB of disk space. The full profile with all 10 services and the dashboard uses around 1.5GB. Docker images are shared where possible.',
  },
  {
    q: 'Is it production-ready?',
    a: 'Evershade is under active development. It is suitable for development and testing workflows. For production use, review the security documentation and consider the current open items in the roadmap.',
  },
  {
    q: 'Can I run it on a VPS?',
    a: 'Yes. Any machine with Docker and at least 2GB of RAM can run the minimal profile. A 4GB+ machine is recommended for the full profile. Evershade is designed to be lightweight and self-hosted.',
  },
  {
    q: 'What models does it support?',
    a: 'Via the Shrewd service, Evershade supports OpenAI (gpt-4o), Anthropic (Claude), Google (Gemini), and any OpenAI-compatible API. Local models via Ollama are also supported for offline use.',
  },
  {
    q: 'How do I update Evershade?',
    a: 'Pull the latest changes from the repository, then rebuild your containers: git pull && docker compose --profile standard up -d --build. The version-manifest.json tracks service versions.',
  },
  {
    q: 'Is my data private?',
    a: 'Yes. All data is stored locally in SQLite databases. The only external calls are to the model APIs you configure. Logs and secrets are redacted by default. No telemetry or analytics are sent.',
  },
] as const

function FaqItem({ q, a, isOpen, onToggle }: { q: string; a: string; isOpen: boolean; onToggle: () => void }) {
  return (
    <div className="border-b border-border">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between py-5 text-left"
        aria-expanded={isOpen}
      >
        <span className="text-base font-semibold tracking-tight">{q}</span>
        {isOpen ? (
          <ChevronUp className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
        ) : (
          <ChevronDown className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
        )}
      </button>
      {isOpen && (
        <div className="pb-5">
          <p className="text-sm leading-snug text-muted-foreground">{a}</p>
        </div>
      )}
    </div>
  )
}

export function Faq() {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  return (
    <section id="faq" aria-labelledby="faq-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="faq-title"
        label="FAQ"
        title={
          <>
            Common
            <span className="text-signal"> questions.</span>
          </>
        }
        lead="Quick answers to the most frequent questions about running Evershade."
      />

      <div className="mt-16 max-w-3xl md:mt-24">
        {FAQ.map((item, i) => (
          <FaqItem
            key={item.q}
            q={item.q}
            a={item.a}
            isOpen={openIndex === i}
            onToggle={() => setOpenIndex(openIndex === i ? null : i)}
          />
        ))}
      </div>
    </section>
  )
}
