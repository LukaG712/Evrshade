import type { Metadata } from 'next'
import { MigrationGuide } from '@/components/site/migration-guide'

export const metadata: Metadata = {
  title: 'Compare — Evershade',
  description: 'Migration guide for moving from other AI coding tools to Evershade.',
}

export default function ComparePage() {
  return (
    <>
      <MigrationGuide />
    </>
  )
}
