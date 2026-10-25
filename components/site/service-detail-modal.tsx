'use client'

import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { X, ChevronRight } from 'lucide-react'
import { SERVICE_DETAILS, type Service } from '@/lib/evershade'
import {
  Brain, Bug, Code2, Database, Eye, Lock, Network, Terminal,
  Webhook, Workflow,
} from 'lucide-react'

const ICONS: Record<string, React.ElementType> = {
  greenie: Workflow,
  slinker: Code2,
  trapper: Bug,
  gobber: Database,
  shrewd: Brain,
  sneaker: Eye,
  hider: Lock,
  poltergeist: Webhook,
  slammer: Network,
  speedy: Terminal,
}

export function ServiceDetailModal({
  service,
  onClose,
}: {
  service: Service
  onClose: () => void
}) {
  const overlayRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleEsc)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = ''
    }
  }, [onClose])

  const details = SERVICE_DETAILS[service.id]
  const Icon = ICONS[service.id]

  if (!details) return null

  const content = (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-background/80 backdrop-blur-sm p-4"
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose()
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="service-modal-title"
    >
      <div className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-xl border border-foreground bg-background p-6 md:p-8">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 inline-flex size-8 items-center justify-center rounded-lg border border-border text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          aria-label="Close"
        >
          <X className="size-4" />
        </button>

        {/* Header */}
        <div className="flex items-start gap-4">
          {Icon && (
            <Icon className="mt-1 size-6 text-muted-foreground" aria-hidden="true" />
          )}
          <div>
            <h2 id="service-modal-title" className="text-2xl font-semibold tracking-tight">
              {service.name}
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">{service.role}</p>
            <div className="mt-2 flex items-center gap-3">
              <span className="font-mono text-xs text-muted-foreground">
                {service.port === 'CLI' ? 'CLI' : `:${service.port}`}
              </span>
              <span className="font-mono text-xs text-muted-foreground">
                {service.stack}
              </span>
            </div>
          </div>
        </div>

        {/* Description */}
        <div className="mt-6 border-t border-border pt-6">
          <p className="text-sm leading-relaxed text-muted-foreground">
            {details.description}
          </p>
        </div>

        {/* Features */}
        {details.features.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Key Features
            </h3>
            <ul className="mt-3 space-y-2">
              {details.features.map((feature, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <ChevronRight className="mt-0.5 size-4 shrink-0 text-signal-ink" aria-hidden="true" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Endpoints */}
        {details.endpoints.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              API Endpoints
            </h3>
            <div className="mt-3 rounded-lg border border-border bg-muted/30 p-4">
              <div className="space-y-1.5">
                {details.endpoints.map((ep, i) => {
                  const parts = ep.split(' — ')
                  const methodPath = parts[0]
                  const desc = parts[1]
                  const [method, ...pathParts] = methodPath.split(' ')
                  const methodColor =
                    method === 'GET' ? 'text-signal-ink' :
                    method === 'POST' ? 'text-amber-500' :
                    method === 'PUT' ? 'text-blue-500' :
                    method === 'DELETE' ? 'text-red-500' :
                    'text-muted-foreground'
                  return (
                    <div key={i} className="flex items-start gap-2 text-xs">
                      <span className={`shrink-0 font-mono font-bold uppercase ${methodColor}`}>
                        {method}
                      </span>
                      <span className="font-mono text-muted-foreground">
                        {pathParts.join(' ')}
                      </span>
                      {desc && (
                        <span className="text-muted-foreground/70">— {desc}</span>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* Dependencies */}
        {details.dependencies.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Dependencies
            </h3>
            <div className="mt-3 flex flex-wrap gap-2">
              {details.dependencies.map((dep, i) => (
                <span
                  key={i}
                  className="inline-flex items-center rounded-md border border-border bg-muted/50 px-2.5 py-1 text-xs font-mono"
                >
                  {dep}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )

  return createPortal(content, document.body)
}
