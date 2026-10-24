import { Brain, Database, Search, GitGraph, ArrowRight, Cpu, FileText, Network } from 'lucide-react'
import { SectionHeading } from './section-heading'

const PIPELINE_STEPS = [
  {
    icon: FileText,
    title: 'Query Ingest',
    description: 'Raw text enters Gobber via the /api/graph/query endpoint. The query is normalized, stop-words removed, and stemmed.',
    detail: 'POST /api/graph/query',
  },
  {
    icon: Cpu,
    title: 'Embedding',
    description: 'The normalized query is vectorized using the configured embedding model (e.g., sentence-transformers). A dense vector represents the semantic meaning.',
    detail: '768-dim vector output',
  },
  {
    icon: Search,
    title: 'Hybrid Search',
    description: 'Two searches run in parallel: BM25 keyword match against the text index, and ANN (Approximate Nearest Neighbor) against the vector store. Results are fused using RRF (Reciprocal Rank Fusion).',
    detail: 'BM25 + ANN → RRF fusion',
  },
  {
    icon: Network,
    title: 'Graph Resolution',
    description: 'Top candidates are expanded through the knowledge graph: entity links, relationships, and transitive connections surface related nodes that keyword search alone would miss.',
    detail: 'Entity → relation → expansion',
  },
  {
    icon: Brain,
    title: 'Context Assembly',
    description: 'Ranked results are assembled into a context window with metadata: source service, timestamp, confidence score, and graph depth. Returned to the caller for LLM consumption.',
    detail: 'Ranked context with metadata',
  },
  {
    icon: Database,
    title: 'Memory Update',
    description: 'New facts extracted from the query response are stored back into the graph, creating a feedback loop. Every mission enriches the knowledge base for the next one.',
    detail: 'Persistent graph growth',
  },
] as const

const GRAPH_ENTITIES = [
  { label: 'Mission m_7f3a', type: 'mission', links: 12 },
  { label: 'Feature: auth-refresh', type: 'feature', links: 8 },
  { label: 'Repo: Evershade', type: 'repository', links: 34 },
  { label: 'Model: gpt-4o', type: 'model', links: 5 },
  { label: 'Error: timeout_408', type: 'error', links: 3 },
  { label: 'User: admin', type: 'user', links: 7 },
] as const

export function KnowledgeGraph() {
  return (
    <section id="knowledge-graph" aria-labelledby="kg-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="kg-title"
        index="17"
        label="Knowledge Graph"
        title={<>Gobber<span className="text-signal">'s</span> memory.</>}
        lead="Every query enriches the system's memory. Gobber combines keyword search, vector embeddings, and graph relationships to surface context that no single method could find alone."
      />

      <div className="mt-16 md:mt-24">
        <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'17.1 — Query pipeline'}</p>
        <ol className="mt-8 grid gap-0 border-t border-foreground">
          {PIPELINE_STEPS.map((step, i) => {
            const Icon = step.icon
            return (
              <li key={step.title} className="group grid items-start gap-6 border-b border-border px-6 py-8 md:grid-cols-[80px_1fr_1fr] md:gap-8">
                <div className="flex items-center gap-3">
                  <span className="flex size-10 items-center justify-center border border-foreground/40 font-mono text-sm tabular-nums text-muted-foreground group-hover:border-signal group-hover:text-signal-ink">
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <Icon className="size-5 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
                </div>
                <div>
                  <p className="text-xl font-semibold tracking-tight">{step.title}</p>
                  <p className="mt-2 text-sm leading-snug text-muted-foreground">{step.description}</p>
                </div>
                <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  <span className="border border-dashed border-foreground/40 px-2 py-1">{step.detail}</span>
                  {i < PIPELINE_STEPS.length - 1 && <ArrowRight className="size-3 opacity-40" aria-hidden="true" />}
                </div>
              </li>
            )
          })}
        </ol>
      </div>

      <div className="mt-24 grid gap-12 md:grid-cols-12 md:gap-8">
        <div className="md:col-span-7">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'17.2 — Graph entities'}</p>
          <ul className="mt-6 grid gap-3 border-t border-foreground sm:grid-cols-2">
            {GRAPH_ENTITIES.map((entity) => (
              <li
                key={entity.label}
                className="group flex items-center justify-between border border-border p-4 transition-colors hover:border-signal"
              >
                <div className="flex items-center gap-3">
                  <GitGraph className="size-4 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
                  <div>
                    <p className="font-mono text-sm tracking-tight">{entity.label}</p>
                    <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{entity.type}</p>
                  </div>
                </div>
                <span className="font-mono text-xs tabular-nums text-muted-foreground">{entity.links} links</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 font-mono text-[10px] text-muted-foreground">
            {'Illustrative entities from a live mission run. The graph grows with every query.'}
          </p>
        </div>

        <div className="md:col-span-4 md:col-start-9">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'17.3 — Why hybrid?'}</p>
          <dl className="mt-6 space-y-4 border-t border-foreground pt-6">
            <div>
              <dt className="font-semibold tracking-tight">Keyword (BM25)</dt>
              <dd className="mt-1 text-sm leading-snug text-muted-foreground">
                {'Exact matches, code identifiers, error codes. Fast and deterministic.'}
              </dd>
            </div>
            <div>
              <dt className="font-semibold tracking-tight">Vector (ANN)</dt>
              <dd className="mt-1 text-sm leading-snug text-muted-foreground">
                {'Semantic similarity. "How do I fix the auth timeout?" finds related docs without exact keywords.'}
              </dd>
            </div>
            <div>
              <dt className="font-semibold tracking-tight">Graph</dt>
              <dd className="mt-1 text-sm leading-snug text-muted-foreground">
                {'Relationships. A mission links to features, features link to repos, repos link to errors. Transitive context.'}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </section>
  )
}
