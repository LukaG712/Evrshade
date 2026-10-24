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
import { SectionDivider } from '@/components/site/section-divider'
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

        {/* 01 — Overview */}
        <SectionDivider index="01" label="Overview" id="overview" />
        <SectionReveal><MissionConsole /></SectionReveal>
        <SectionReveal><MissionControl /></SectionReveal>

        {/* 02 — How It Works */}
        <SectionDivider index="02" label="How It Works" id="how-it-works" />
        <SectionReveal><RequestTrace /></SectionReveal>
        <SectionReveal><Architecture /></SectionReveal>
        <SectionReveal><KnowledgeGraph /></SectionReveal>

        {/* 03 — Platform */}
        <SectionDivider index="03" label="Platform" id="platform" />
        <SectionReveal><Harness /></SectionReveal>
        <SectionReveal><Security /></SectionReveal>
        <SectionReveal><Integrations /></SectionReveal>
        <SectionReveal><SlammerPreview /></SectionReveal>

        {/* 04 — Get Started */}
        <SectionDivider index="04" label="Get Started" id="get-started" />
        <SectionReveal><Cli /></SectionReveal>
        <SectionReveal><Install /></SectionReveal>
        <SectionReveal><UseCases /></SectionReveal>

        {/* 05 — About */}
        <SectionDivider index="05" label="About" id="about" />
        <SectionReveal><Comparison /></SectionReveal>
        <SectionReveal><PerformanceMetrics /></SectionReveal>
        <SectionReveal><ApiReference /></SectionReveal>

        {/* 06 — Roadmap */}
        <SectionDivider index="06" label="Roadmap" id="roadmap" />
        <SectionReveal><ChangelogTicker /></SectionReveal>
        <SectionReveal><Roadmap /></SectionReveal>
        <SectionReveal><Community /></SectionReveal>
      </main>
      <Footer />
    </>
  )
}
