import type { Metadata } from 'next'
import { ConfigReference } from '@/components/site/config-reference'
import { Glossary } from '@/components/site/glossary'
import { ProjectLayout } from '@/components/site/project-layout'

export const metadata: Metadata = {
  title: 'Configuration — Evershade Docs',
  description: 'Environment variables, glossary of terms, and project layout for Evershade.',
}

export default function ConfigurationPage() {
  return (
    <>
      <ConfigReference />
      <Glossary />
      <ProjectLayout />
    </>
  )
}
