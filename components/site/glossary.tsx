import { SectionHeading } from './section-heading'

const TERMS = [
  { term: 'Mission', def: 'A large task broken into milestones and features. Missions are planned, executed, validated, and completed through the Mission Control lifecycle.' },
  { term: 'Milestone', def: 'A group of related features within a mission. Milestones run their features with parallel workers.' },
  { term: 'Feature', def: 'The smallest unit of work. A feature is a single change that can be planned, executed, and validated independently.' },
  { term: 'Agent', def: 'An AI-powered worker that executes features. Agents have their own isolated environment, tools, and optionally a browser.' },
  { term: 'Harness', def: 'The reusable workflow engine that orchestrates agents, subagents, and event-driven automation.' },
  { term: 'Approval gate', def: 'A human-in-the-loop checkpoint where sensitive operations require explicit user approval before proceeding.' },
  { term: 'Autonomy level', def: 'A dial that controls how much agents can act without human intervention: full, partial, or none.' },
  { term: 'Knowledge graph', def: 'Gobber\'s persistent memory system that combines keyword search, vector embeddings, and graph relationships.' },
  { term: 'Plugin', def: 'An MCP tool extension that adds new capabilities to the platform without modifying core services.' },
  { term: 'Profile', def: 'A preset configuration that determines which services are installed: minimal, standard, full, or custom.' },
  { term: 'SSE', def: 'Server-Sent Events. Real-time streaming of mission execution logs from the server to the dashboard.' },
  { term: 'Workstation', def: 'An isolated Linux environment with its own filesystem, shell, tools, and optionally a browser and full desktop.' },
]

export function Glossary() {
  return (
    <section id="glossary" aria-labelledby="glossary-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="glossary-title"
        label="Glossary"
        title={
          <>
            Learn the language,
            <br />
            <span className="text-muted-foreground">quickly.</span>
          </>
        }
      />

      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {TERMS.map((t) => (
          <div key={t.term} className="border border-foreground p-5">
            <p className="font-semibold tracking-tight">{t.term}</p>
            <p className="mt-2 text-sm leading-snug text-muted-foreground">{t.def}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
