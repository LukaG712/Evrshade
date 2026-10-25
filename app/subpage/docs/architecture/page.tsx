import type { Metadata } from 'next'
import { Architecture } from '@/components/site/architecture'
import { RequestTrace } from '@/components/site/request-trace'
import { KnowledgeGraph } from '@/components/site/knowledge-graph'

export const metadata: Metadata = {
  title: 'Architecture — Evershade Docs',
  description: 'Deep dive into Evershade\'s microservices architecture, request lifecycle, and knowledge graph.',
}

export default function ArchitecturePage() {
  return (
    <>
      <Architecture />
      <RequestTrace />
      <KnowledgeGraph />
    </>
  )
}
