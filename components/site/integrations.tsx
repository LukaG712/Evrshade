import { INTEGRATIONS } from '@/lib/evershade'
import { cn } from '@/lib/utils'
import { SectionHeading } from './section-heading'

export function Integrations() {
  return (
    <section id="integrations" aria-labelledby="integrations-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="integrations-title"
        label="Integrations"
        title={
          <>
            Bring your models<span className="text-signal">.</span>
            <br />
            <span className="text-muted-foreground">Keep your stack.</span>
          </>
        }
        lead="Each integration lives behind exactly one service, so swapping a provider never ripples through the platform. Ollama keeps everything on your machine."
      />

      <ul className="mt-16 grid border-t border-l border-foreground md:mt-24 md:grid-cols-2 xl:grid-cols-3">
        {INTEGRATIONS.map((g, gi) => (
          <li key={g.group} className="flex flex-col border-r border-b border-foreground p-6 md:p-8">
            <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-wider">
              <span className="text-muted-foreground">{`I.${String(gi + 1).padStart(2, '0')}`}</span>
              <span className="flex items-center gap-1.5">
                <span className="text-muted-foreground">{'via'}</span>
                <span className="bg-foreground px-1.5 py-0.5 text-background">{g.via}</span>
              </span>
            </div>
            <p className="mt-10 text-3xl font-semibold tracking-tight md:text-4xl">{g.group}</p>
            <p className="mt-2 text-pretty leading-snug text-muted-foreground">{g.detail}</p>
            <ul className="mt-8 border-t border-foreground md:mt-auto md:pt-0">
              {g.items.map((item) => (
                <li key={`${item.name}-${item.note ?? ''}`} className="flex items-center justify-between gap-3 border-b border-border py-2.5">
                  <span className="text-base font-medium">
                    {item.name}
                    {item.note ? <span className="ml-2 font-mono text-[11px] font-normal text-muted-foreground">{item.note}</span> : null}
                  </span>
                  <span
                    className={cn(
                      'font-mono text-[10px] uppercase tracking-wider',
                      item.status === 'shipped' ? 'text-signal-ink' : 'border border-dashed border-foreground/40 px-1.5 py-0.5 text-muted-foreground',
                    )}
                  >
                    {item.status === 'shipped' ? '● shipped' : 'extensible'}
                  </span>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
      <p className="mt-4 font-mono text-[11px] text-muted-foreground">
        {'“Extensible” means the interface exists but a built-in adapter does not ship today.'}
      </p>
    </section>
  )
}
