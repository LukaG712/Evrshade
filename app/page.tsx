import { dynamic } from 'next/dynamic'
import { ApiReference } from '@/components/site/api-reference'
import { Architecture } from '@/components/site/architecture'
import { ChangelogTicker } from '@/components/site/changelog-ticker'
import { Community } from '@/components/site/community'
import { Comparison } from '@/components/site/comparison'
import { ConfigReference } from '@/components/site/config-reference'
import { DockerCompose } from '@/components/site/docker-compose'
import { Footer } from '@/components/site/footer'
import { Glossary } from '@/components/site/glossary'
import { Harness } from '@/components/site/harness'
import { Header } from '@/components/site/header'
import { Hero } from '@/components/site/hero'
import { Integrations } from '@/components/site/integrations'
import { KnowledgeGraph } from '@/components/site/knowledge-graph'
import { MissionControl } from '@/components/site/mission-control'
import { PerformanceMetrics } from '@/components/site/performance-metrics'
import { ProjectLayout } from '@/components/site/project-layout'
import { RequestTrace } from '@/components/site/request-trace'
import { Roadmap } from '@/components/site/roadmap'
import { SectionDivider } from '@/components/site/section-divider'
import { Security } from '@/components/site/security'
import { ServicesGrid } from '@/components/site/services-grid'
import { SlammerPreview } from '@/components/site/slammer-preview'
import { TryIt } from '@/components/site/try-it'
import { UseCases } from '@/components/site/use-cases'

// Lazy-load heavy interactive components that are below the fold
const BackToTop = dynamic(() => import('@/components/site/back-to-top').then(m => ({ default: m.BackToTop })), { ssr: false })
const Cli = dynamic(() => import('@/components/site/cli').then(m => ({ default: m.Cli })), { ssr: false })
const Faq = dynamic(() => import('@/components/site/faq').then(m => ({ default: m.Faq })), { ssr: false })
const Install = dynamic(() => import('@/components/site/install').then(m => ({ default: m.Install })), { ssr: false })
const MissionConsole = dynamic(() => import('@/components/site/mission-console').then(m => ({ default: m.MissionConsole })), { ssr: false })
const ScrollProgress = dynamic(() => import('@/components/site/scroll-progress').then(m => ({ default: m.ScrollProgress })), { ssr: false })
const SectionReveal = dynamic(() => import('@/components/site/section-reveal').then(m => ({ default: m.SectionReveal })), { ssr: false })

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
