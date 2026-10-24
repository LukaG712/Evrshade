'use client'

import { ChevronDown, ChevronUp, HelpCircle } from 'lucide-react'
import { useState } from 'react'
import { SectionHeading } from './section-heading'

const FAQ = [
  {
    q: 'Do I need a GPU?',
    a: 'For cloud models like GPT-4 or Claude, no — all processing happens on the provider servers, so any machine works. For local models via Ollama, a GPU is not required but strongly recommended: without one, models run on CPU and will be noticeably slower, especially for larger models (7B+ parameters). A mid-range NVIDIA GPU (GTX 1660 or better) makes local models practical for everyday use.',
  },
  {
    q: 'Is Evershade free?',
    a: 'Evershade itself is free and open-source under the MIT license. You can self-host it at no cost. However, using cloud AI models (OpenAI, Anthropic, Google) requires your own API key and billing with those providers. Local models via Ollama are free to run on your hardware. Note: this pricing model may change in the future. The core platform will remain open-source, but commercial tiers could be introduced.',
  },
  {
    q: 'Can I use my own API key?',
    a: 'Yes. You provide your own API keys for whichever models you want to use. Evershade never stores or transmits your keys anywhere except to the model provider you configure. Your data stays on your machine except for the explicit model API calls you make.',
  },
  {
    q: 'How much disk space does it need?',
    a: 'The minimal profile (4 core services) uses about 500MB. The full profile with all 10 services and the dashboard uses around 1.5GB. If you run local models via Ollama, add 4-8GB per model depending on size. Docker images share layers where possible to save space.',
  },
  {
    q: 'Is it production-ready?',
    a: 'Evershade is under active development and best suited for development and testing workflows right now. Core services are stable, but some features are still being built. For production use, review the security docs, test thoroughly in your environment, and check the roadmap for open items.',
  },
  {
    q: 'Can I run it on a VPS?',
    a: 'Yes. A VPS with Docker and at least 2GB of RAM can run the minimal profile. For the full profile with all services, 4GB+ RAM is recommended. If you want to run local models, you will need a GPU-enabled VPS — most standard VPS providers do not offer GPUs, so cloud models are more practical for that use case.',
  },
  {
    q: 'What models does it support?',
    a: 'Via the Shrewd service, Evershade supports OpenAI (GPT-4o, GPT-3.5), Anthropic (Claude), Google (Gemini), and any OpenAI-compatible API endpoint. For offline use, local models via Ollama are supported — you can run models like Llama 3, Mistral, or Phi directly on your hardware.',
  },
  {
    q: 'How do I update Evershade?',
    a: 'Pull the latest code and rebuild: git pull && docker compose --profile standard up -d --build. The version-manifest.json file tracks which version each service is running. Always check the changelog before updating to see what changed.',
  },
  {
    q: 'Is my data private?',
    a: 'Yes. All data is stored locally in SQLite databases on your machine. The only external calls are to the model APIs you explicitly configure. Logs and secrets are redacted by default, and Evershade sends no telemetry or analytics. You own everything.',
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
