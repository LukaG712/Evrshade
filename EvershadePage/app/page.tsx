import { Architecture } from '@/components/site/architecture'
import { Cli } from '@/components/site/cli'
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
        <Roadmap />
      </main>
      <Footer />
    </>
  )
}
