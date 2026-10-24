import type { Metadata } from 'next'
import { Install } from '@/components/site/install'
import { Cli } from '@/components/site/cli'
import { DockerCompose } from '@/components/site/docker-compose'
import { SystemRequirements } from '@/components/site/system-requirements'
import { Faq } from '@/components/site/faq'

export const metadata: Metadata = {
  title: 'Install Evershade — Self-hosted AI agent platform',
  description: 'Step-by-step guide to installing Evershade. System requirements, one-liner install script, Docker Compose setup, and troubleshooting.',
}

export default function InstallPage() {
  return (
    <>
      <Install />
      <Cli />
      <DockerCompose />
      <SystemRequirements />
      <Faq />
    </>
  )
}
