import { BookOpen } from 'lucide-react'
import { SectionHeading } from './section-heading'

const GLOSSARY = [
  { term: 'Mission', def: 'A top-level task broken into milestones and features. Example: "Refactor the authentication module."' },
  { term: 'Milestone', def: 'A phase within a mission. Each milestone contains one or more features that run in parallel.' },
  { term: 'Feature', def: 'The smallest unit of work. A feature is executed, validated, and either passes or enters the fix loop.' },
  { term: 'Droid', def: 'An automated agent that executes features inside containers or workstations for isolation.' },
  { term: 'Harness', def: 'The framework that manages droids, skills, and workstations. It handles scheduling, isolation, and recovery.' },
  { term: 'Approval gate', def: 'A pause point where human review is required before a sensitive operation proceeds.' },
] as const

export function Glossary() {
  return (
    <section id="glossary" aria-labelledby="glossary-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="glossary-title"
        label="Glossary"
        title={
          <>
            Learn the
            <span className="text-signal"> language.</span>
          </>
        }
        lead="Evershade uses specific terms for its concepts. Here's what they mean."
      />

      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 md:mt-24">
        {GLOSSARY.map((item) => (
          <div
            key={item.term}
            className="group border border-border p-5 transition-colors hover:border-signal"
          >
            <div className="flex items-center gap-2">
              <BookOpen className="size-4 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
              <p className="font-semibold tracking-tight">{item.term}</p>
            </div>
            <p className="mt-3 text-sm leading-snug text-muted-foreground">{item.def}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
