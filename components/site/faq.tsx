'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { SectionHeading } from './section-heading'

const FAQ = [
  {
    q: 'Do I need a GPU?',
    a: (
      <>
        <strong className="font-semibold text-foreground">No.</strong>{' '}
        Evershade runs on ordinary developer hardware. All LLM inference happens over the network through Shrewd, the model routing service, so no local GPU is required. You only need enough CPU and RAM to run the service processes — even a modest laptop will handle it. If you want to run models locally via Ollama, a GPU helps but is still optional.
      </>
    ),
  },
  {
    q: 'Can I run just some services?',
    a: (
      <>
        <strong className="font-semibold text-foreground">Yes, Evershade is fully modular.</strong>{' '}
        Installation profiles let you pick exactly which services you need. The <code className="rounded bg-muted px-1 text-xs">minimal</code> profile runs just the 4 core services (Greenie, Slinker, Sneaker, Shrewd). The <code className="rounded bg-muted px-1 text-xs">standard</code> profile adds optional services like Gobber and Trapper but excludes the dashboard. The <code className="rounded bg-muted px-1 text-xs">full</code> profile includes everything, including the Slammer dashboard. You can also create a <code className="rounded bg-muted px-1 text-xs">custom</code> profile to enable only the services you want.
      </>
    ),
  },
  {
    q: 'Is my data safe?',
    a: (
      <>
        <strong className="font-semibold text-foreground">Everything stays on your machine.</strong>{' '}
        No telemetry is sent. Cloud models are optional — you can run entirely offline with local models. Secrets (API keys, tokens) are encrypted with AES-256-GCM at rest in the Hider service. All databases are local SQLite files. The only network traffic is the LLM API calls you explicitly configure, and even those are optional if you use local models.
      </>
    ),
  },
  {
    q: 'Which LLM providers are supported?',
    a: (
      <>
        <strong className="font-semibold text-foreground">Any provider with an OpenAI-compatible API.</strong>{' '}
        Shrewd abstracts the provider layer, so you can swap between providers without changing your mission configuration. Supported out of the box: OpenAI, Anthropic, Ollama, and any OpenAI-compatible endpoint (vLLM, LM Studio, etc.). You configure providers in your <code className="rounded bg-muted px-1 text-xs">.env</code> file with API keys and base URLs. Shrewd also handles model routing, fallback, and cost tracking across providers.
      </>
    ),
  },
  {
    q: 'Can I use local models?',
    a: (
      <>
        <strong className="font-semibold text-foreground">Yes, with zero external API calls.</strong>{' '}
        The Ollama profile lets you run models entirely on your machine. Install Ollama, pull your preferred model, and configure Shrewd to point to your local Ollama endpoint. All inference stays local — no data leaves your machine. Performance depends on your hardware; a GPU helps but smaller models run fine on CPU. This is the most privacy-preserving setup.
      </>
    ),
  },
  {
    q: 'How do I update?',
    a: (
      <>
        <strong className="font-semibold text-foreground">Pull and restart.</strong>{' '}
        Pull the latest changes from each service repository and restart with <code className="rounded bg-muted px-1 text-xs">./start.sh</code>. The CLI handles version compatibility checks between services, so you won't accidentally mix incompatible versions. Database migrations run automatically on startup if schema changes are needed. Check the changelog page for breaking changes before updating.
      </>
    ),
  },
  {
    q: 'Is there a web UI?',
    a: (
      <>
        <strong className="font-semibold text-foreground">Yes, the Slammer dashboard.</strong>{' '}
        Slammer is a React-based web dashboard that gives you full visibility into your Evershade instance. You can monitor mission progress, approve or deny operations before they execute, watch agents work in real time, review logs from all services, and manage configuration. It runs on port 5173 by default and is included in the <code className="rounded bg-muted px-1 text-xs">full</code> installation profile.
      </>
    ),
  },
  {
    q: 'What about backups?',
    a: (
      <>
        <strong className="font-semibold text-foreground">Back up the data directory.</strong>{' '}
        All persistent data is stored in SQLite databases under a single data directory. Copying that directory gives you a complete snapshot of your Evershade instance — missions, configurations, secrets, knowledge graph, everything. For safety, stop the services before copying to avoid partial writes. You can automate backups with a simple cron job or script that archives the data directory.
      </>
    ),
  },
]

export function Faq() {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <section id="faq" aria-labelledby="faq-title" className="px-6 pt-20 md:pt-32">
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

      <div className="mt-8">
        {FAQ.map((item, i) => (
          <div key={item.q} className="border-b border-border">
            <button
              type="button"
              onClick={() => setOpen(open === i ? null : i)}
              className="flex w-full items-center justify-between py-3 text-left font-semibold tracking-tight"
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
              <p className="pb-3 text-sm leading-snug text-muted-foreground">{item.a}</p>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
