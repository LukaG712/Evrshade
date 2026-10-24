import dynamic from 'next/dynamic'
import { Footer } from '@/components/site/footer'
import { Header } from '@/components/site/header'
import { Hero } from '@/components/site/hero'
import { MobileToc } from '@/components/site/mobile-toc'
import { SectionDivider } from '@/components/site/section-divider'
import { SectionReveal } from '@/components/site/section-reveal'

// Always-visible: load immediately
const ServicesGrid = dynamic(() => import('@/components/site/services-grid').then(m => ({ default: m.ServicesGrid })))
const MissionConsole = dynamic(() => import('@/components/site/mission-console').then(m => ({ default: m.MissionConsole })))
const MissionControl = dynamic(() => import('@/components/site/mission-control').then(m => ({ default: m.MissionControl })))

// Below-the-fold: lazy load
const RequestTrace = dynamic(() => import('@/components/site/request-trace').then(m => ({ default: m.RequestTrace })))
const Architecture = dynamic(() => import('@/components/site/architecture').then(m => ({ default: m.Architecture })))
const KnowledgeGraph = dynamic(() => import('@/components/site/knowledge-graph').then(m => ({ default: m.KnowledgeGraph })))
const ProjectLayout = dynamic(() => import('@/components/site/project-layout').then(m => ({ default: m.ProjectLayout })))
const Harness = dynamic(() => import('@/components/site/harness').then(m => ({ default: m.Harness })))
const Security = dynamic(() => import('@/components/site/security').then(m => ({ default: m.Security })))
const Integrations = dynamic(() => import('@/components/site/integrations').then(m => ({ default: m.Integrations })))
const SlammerPreview = dynamic(() => import('@/components/site/slammer-preview').then(m => ({ default: m.SlammerPreview })))
const ConfigReference = dynamic(() => import('@/components/site/config-reference').then(m => ({ default: m.ConfigReference })))
const SystemRequirements = dynamic(() => import('@/components/site/system-requirements').then(m => ({ default: m.SystemRequirements })))
const TryIt = dynamic(() => import('@/components/site/try-it').then(m => ({ default: m.TryIt })))
const DockerCompose = dynamic(() => import('@/components/site/docker-compose').then(m => ({ default: m.DockerCompose })))
const Cli = dynamic(() => import('@/components/site/cli').then(m => ({ default: m.Cli })))
const Install = dynamic(() => import('@/components/site/install').then(m => ({ default: m.Install })))
const UseCases = dynamic(() => import('@/components/site/use-cases').then(m => ({ default: m.UseCases })))
const Comparison = dynamic(() => import('@/components/site/comparison').then(m => ({ default: m.Comparison })))
const MigrationGuide = dynamic(() => import('@/components/site/migration-guide').then(m => ({ default: m.MigrationGuide })))
const Pricing = dynamic(() => import('@/components/site/pricing').then(m => ({ default: m.Pricing })))
const PerformanceMetrics = dynamic(() => import('@/components/site/performance-metrics').then(m => ({ default: m.PerformanceMetrics })))
const ApiReference = dynamic(() => import('@/components/site/api-reference').then(m => ({ default: m.ApiReference })))
const Glossary = dynamic(() => import('@/components/site/glossary').then(m => ({ default: m.Glossary })))
const Faq = dynamic(() => import('@/components/site/faq').then(m => ({ default: m.Faq })))
const Testimonials = dynamic(() => import('@/components/site/testimonials').then(m => ({ default: m.Testimonials })))
const Changelog = dynamic(() => import('@/components/site/changelog').then(m => ({ default: m.Changelog })))
const Roadmap = dynamic(() => import('@/components/site/roadmap').then(m => ({ default: m.Roadmap })))
const Contributing = dynamic(() => import('@/components/site/contributing').then(m => ({ default: m.Contributing })))
const Community = dynamic(() => import('@/components/site/community').then(m => ({ default: m.Community })))

export default function Page() {
  return (
    <>
      <Header />
      <MobileToc />
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
        <SectionReveal><SystemRequirements /></SectionReveal>
        <SectionReveal><TryIt /></SectionReveal>
        <SectionReveal><DockerCompose /></SectionReveal>
        <SectionReveal><Cli /></SectionReveal>
        <SectionReveal><Install /></SectionReveal>
        <SectionReveal><UseCases /></SectionReveal>

        {/* 05 — About */}
        <SectionDivider index="05" label="About" id="about" />
        <SectionReveal><Comparison /></SectionReveal>
        <SectionReveal><MigrationGuide /></SectionReveal>
        <SectionReveal><Pricing /></SectionReveal>
        <SectionReveal><PerformanceMetrics /></SectionReveal>
        <SectionReveal><ApiReference /></SectionReveal>
        <SectionReveal><Glossary /></SectionReveal>
        <SectionReveal><Faq /></SectionReveal>
        <SectionReveal><Testimonials /></SectionReveal>

        {/* 06 — Roadmap */}
        <SectionDivider index="06" label="Roadmap" id="roadmap" />
        <SectionReveal><Changelog /></SectionReveal>
        <SectionReveal><Roadmap /></SectionReveal>
        <SectionReveal><Contributing /></SectionReveal>
        <SectionReveal><Community /></SectionReveal>
      </main>
      <Footer />
    </>
  )
}
