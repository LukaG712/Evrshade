import { ApiReference } from '@/components/site/api-reference'
import { Architecture } from '@/components/site/architecture'
import { BackToTop } from '@/components/site/back-to-top'
import { ChangelogTicker } from '@/components/site/changelog-ticker'
import { Cli } from '@/components/site/cli'
import { Community } from '@/components/site/community'
import { Comparison } from '@/components/site/comparison'
import { ConfigReference } from '@/components/site/config-reference'
import { DockerCompose } from '@/components/site/docker-compose'
import { Download } from '@/components/site/download'
import { Faq } from '@/components/site/faq'
import { Footer } from '@/components/site/footer'
import { Glossary } from '@/components/site/glossary'
import { Harness } from '@/components/site/harness'
import { Header } from '@/components/site/header'
import { Hero } from '@/components/site/hero'
import { Install } from '@/components/site/install'
import { Integrations } from '@/components/site/integrations'
import { KnowledgeGraph } from '@/components/site/knowledge-graph'
import { MissionConsole } from '@/components/site/mission-console'
import { MissionControl } from '@/components/site/mission-control'
import { PerformanceMetrics } from '@/components/site/performance-metrics'
import { ProjectLayout } from '@/components/site/project-layout'
import { RequestTrace } from '@/components/site/request-trace'
import { Roadmap } from '@/components/site/roadmap'
import { ScrollProgress } from '@/components/site/scroll-progress'
import { SectionDivider } from '@/components/site/section-divider'
import { SectionReveal } from '@/components/site/section-reveal'
import { Security } from '@/components/site/security'
import { ServicesGrid } from '@/components/site/services-grid'
import { SlammerPreview } from '@/components/site/slammer-preview'
import { SystemRequirements } from '@/components/site/system-requirements'
import { TryIt } from '@/components/site/try-it'
import { UseCases } from '@/components/site/use-cases'

export default function Page() {
  return (
    <>
      <ScrollProgress />
      <BackToTop />
      <Header />
      <main id="top">
        <Hero />

        {/* 01 — Overview */}
        <SectionDivider index="01" label="Overview" id="overview" />
        <SectionReveal><ServicesGrid /></SectionReveal>
        <SectionReveal><MissionConsole /></SectionReveal>
        <SectionReveal><MissionControl /></SectionReveal>

        {/* 02 — How It Works */}
        <SectionDivider index="02" label="How It Works" id="how-it-works" />
        <SectionReveal><RequestTrace /></SectionReveal>
        <SectionReveal><Architecture /></SectionReveal>
        <SectionReveal><KnowledgeGraph /></SectionReveal>
        <SectionReveal><ProjectLayout /></SectionReveal>

        {/* 03 — Platform */}
        <SectionDivider index="03" label="Platform" id="platform" />
        <SectionReveal><Harness /></SectionReveal>
        <SectionReveal><Security /></SectionReveal>
        <SectionReveal><Integrations /></SectionReveal>
        <SectionReveal><SlammerPreview /></SectionReveal>
        <SectionReveal><ConfigReference /></SectionReveal>

        {/* 04 — Get Started */}
        <SectionDivider index="04" label="Get Started" id="get-started" />
        <SectionReveal><Download /></SectionReveal>
        <SectionReveal><SystemRequirements /></SectionReveal>
        <SectionReveal><TryIt /></SectionReveal>
        <SectionReveal><DockerCompose /></SectionReveal>
        <SectionReveal><Cli /></SectionReveal>
        <SectionReveal><Install /></SectionReveal>
        <SectionReveal><UseCases /></SectionReveal>

        {/* 05 — About */}
        <SectionDivider index="05" label="About" id="about" />
        <SectionReveal><Comparison /></SectionReveal>
        <SectionReveal><PerformanceMetrics /></SectionReveal>
        <SectionReveal><ApiReference /></SectionReveal>
        <SectionReveal><Glossary /></SectionReveal>
        <SectionReveal><Faq /></SectionReveal>

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
