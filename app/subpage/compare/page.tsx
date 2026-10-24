import type { Metadata } from 'next'
import { Comparison } from '@/components/site/comparison'
import { MigrationGuide } from '@/components/site/migration-guide'

export const metadata: Metadata = {
  title: 'Compare — Evershade',
  description: 'Compare Evershade with Cursor, Copilot, Aider, and OpenDevin. Feature comparison table and migration guide.',
}

export default function ComparePage() {
  return (
    <>
      <Comparison />
      <MigrationGuide />
    </>
  )
}
