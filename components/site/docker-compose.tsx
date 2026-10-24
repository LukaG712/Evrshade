'use client'

import { Check, Copy } from 'lucide-react'
import { useState } from 'react'
import { SectionHeading } from './section-heading'

const COMPOSE = `version: '3.8'

services:
  greenie:
    image: evershade/greenie:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=sqlite:///data/greenie.db
    volumes:
      - ./data:/data

  slinker:
    image: evershade/slinker:latest
    ports:
      - "8000:8000"

  trapper:
    image: evershade/trapper:latest
    ports:
      - "3000:3000"

  gobber:
    image: evershade/gobber:latest
    ports:
      - "8085:8085"
    volumes:
      - ./data:/data`

export function DockerCompose() {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    await navigator.clipboard.writeText(COMPOSE)
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }

  return (
    <section id="docker-compose" aria-labelledby="docker-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="docker-title"
        label="Docker Compose"
        title={
          <>
            Up and running,
            <br />
            <span className="text-muted-foreground">in one command.</span>
          </>
        }
        lead="Every service runs in its own container. No Kubernetes, no Kafka, no distributed databases."
      />

      <div className="mt-16 border border-foreground">
        <div className="flex items-center justify-between border-b border-foreground px-4 py-2.5">
          <span className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">docker-compose.yml</span>
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
          <code>{COMPOSE}</code>
        </pre>
      </div>
    </section>
  )
}
