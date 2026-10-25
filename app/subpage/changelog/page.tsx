import type { Metadata } from 'next'
import { Changelog } from '@/components/site/changelog'
import { Roadmap } from '@/components/site/roadmap'

export const metadata: Metadata = {
  title: 'Changelog — Evershade',
  description: 'Evershade development timeline, changelog, and the product roadmap.',
}

export default function ChangelogPage() {
  return (
    <>
      <Changelog />
      <Roadmap />
    </>
  )
}
