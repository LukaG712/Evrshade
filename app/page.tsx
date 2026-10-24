import { ApiReference } from '@/components/site/api-reference'
import { Architecture } from '@/components/site/architecture'
import { ChangelogTicker } from '@/components/site/changelog-ticker'
import { Cli } from '@/components/site/cli'
import { Community } from '@/components/site/community'
import { Comparison } from '@/components/site/comparison'
import { Footer } from '@/components/site/footer'
import { Harness } from '@/components/site/harness'
import { Header } from '@/components/site/header'
import { Hero } from '@/components/site/hero'
import { Install } from '@/components/site/install'
import { Integrations } from '@/components/site/integrations'
import { KnowledgeGraph } from '@/components/site/knowledge-graph'
import { MissionConsole } from '@/components/site/mission-console'
import { MissionControl } from '@/components/site/mission-control'
import { PerformanceMetrics } from '@/components/site/performance-metrics'
import { RequestTrace } from '@/components/site/request-trace'
import { Roadmap } from '@/components/site/roadmap'
import { SectionReveal } from '@/components/site/section-reveal'
import { Security } from '@/components/site/security'
import { SlammerPreview } from '@/components/site/slammer-preview'
import { UseCases } from '@/components/site/use-cases'

export default function Page() {
  return (
    <>
      <Header />
      <main id="top">
        <Hero />
        <SectionReveal><MissionConsole /></SectionReveal>
        <SectionReveal><MissionControl /></SectionReveal>
        <SectionReveal><RequestTrace /></SectionReveal>
        <SectionReveal><Harness /></SectionReveal>
        <SectionReveal><Security /></SectionReveal>
        <SectionReveal><Architecture /></SectionReveal>
        <SectionReveal><Integrations /></SectionReveal>
        <SectionReveal><Cli /></SectionReveal>
        <SectionReveal><Install /></SectionReveal>
        <SectionReveal><ChangelogTicker /></SectionReveal>
        <SectionReveal><Roadmap /></SectionReveal>
        <SectionReveal><ApiReference /></SectionReveal>
        <SectionReveal><Comparison /></SectionReveal>
        <SectionReveal><UseCases /></SectionReveal>
        <SectionReveal><SlammerPreview /></SectionReveal>
        <SectionReveal><KnowledgeGraph /></SectionReveal>
        <SectionReveal><PerformanceMetrics /></SectionReveal>
        <SectionReveal><Community /></SectionReveal>
      </main>
      <Footer />
    </>
  )
}
