import { ApiReference } from '@/components/site/api-reference'
import { Architecture } from '@/components/site/architecture'
import { ChangelogTicker } from '@/components/site/changelog-ticker'
import { Cli } from '@/components/site/cli'
import { Comparison } from '@/components/site/comparison'
import { Footer } from '@/components/site/footer'
import { Harness } from '@/components/site/harness'
import { Header } from '@/components/site/header'
import { Hero } from '@/components/site/hero'
import { Install } from '@/components/site/install'
import { Integrations } from '@/components/site/integrations'
import { MissionConsole } from '@/components/site/mission-console'
import { MissionControl } from '@/components/site/mission-control'
import { RequestTrace } from '@/components/site/request-trace'
import { Roadmap } from '@/components/site/roadmap'
import { Security } from '@/components/site/security'
import { SlammerPreview } from '@/components/site/slammer-preview'
import { UseCases } from '@/components/site/use-cases'

export default function Page() {
  return (
    <>
      <Header />
      <main id="top">
        <Hero />
        <MissionConsole />
        <MissionControl />
        <RequestTrace />
        <Harness />
        <Security />
        <Architecture />
        <Integrations />
        <Cli />
        <Install />
        <ChangelogTicker />
        <Roadmap />
        <ApiReference />
        <Comparison />
        <UseCases />
        <SlammerPreview />
      </main>
      <Footer />
    </>
  )
}
