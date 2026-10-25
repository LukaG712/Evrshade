import dynamic from 'next/dynamic'
import { BackToTop } from '@/components/site/back-to-top'
import { LoadingScreen } from '@/components/site/loading-screen'
import { Architecture } from '@/components/site/architecture'
import { Cli } from '@/components/site/cli'
import { Faq } from '@/components/site/faq'
import { Footer } from '@/components/site/footer'
import { HapticFeedback } from '@/components/site/haptic-feedback'
import { Harness } from '@/components/site/harness'
import { Header } from '@/components/site/header'
import { Hero } from '@/components/site/hero'
import { Install } from '@/components/site/install'
import { Integrations } from '@/components/site/integrations'
import { KnowledgeGraph } from '@/components/site/knowledge-graph'
import { MissionConsole } from '@/components/site/mission-console'
import { MobileToc } from '@/components/site/mobile-toc'
import { PerformanceMetrics } from '@/components/site/performance-metrics'
import { RequestTrace } from '@/components/site/request-trace'
import { SectionDivider } from '@/components/site/section-divider'
import { SectionReveal } from '@/components/site/section-reveal'
import { Security } from '@/components/site/security'
import { SlammerPreview } from '@/components/site/slammer-preview'
import { SwipeNavigation } from '@/components/site/swipe-navigation'
import { UseCases } from '@/components/site/use-cases'

// Lazy-load components further down the page
const ApiReference = dynamic(() => import('@/components/site/api-reference').then(m => ({ default: m.ApiReference })))
const Community = dynamic(() => import('@/components/site/community').then(m => ({ default: m.Community })))
const KnownLimitations = dynamic(() => import('@/components/site/known-limitations').then(m => ({ default: m.KnownLimitations })))
const Roadmap = dynamic(() => import('@/components/site/roadmap').then(m => ({ default: m.Roadmap })))
const SystemRequirements = dynamic(() => import('@/components/site/system-requirements').then(m => ({ default: m.SystemRequirements })))

export default function Page() {
  return (
    <>
      <LoadingScreen />
      <Header />
      <SwipeNavigation />
      <HapticFeedback />
      <MobileToc />
      <BackToTop />
      <main id="top">
        <Hero />

        {/* 01 — Overview */}
        <SectionDivider index="01" label="Overview" id="overview" />
        <SectionReveal><MissionConsole /></SectionReveal>

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
        <SectionReveal><SystemRequirements /></SectionReveal>
        <SectionReveal><Cli /></SectionReveal>
        <SectionReveal><Install /></SectionReveal>
        <SectionReveal><UseCases /></SectionReveal>
        <SectionReveal><Faq /></SectionReveal>

        {/* 05 — About */}
        <SectionDivider index="05" label="About" id="about" />
        <SectionReveal><PerformanceMetrics /></SectionReveal>
        <SectionReveal><ApiReference /></SectionReveal>
        <SectionReveal><KnownLimitations /></SectionReveal>

        {/* 06 — Roadmap */}
        <SectionDivider index="06" label="Roadmap" id="roadmap" />
        <SectionReveal><Roadmap /></SectionReveal>
        <SectionReveal><Community /></SectionReveal>
      </main>
      <Footer />
    </>
  )
}
