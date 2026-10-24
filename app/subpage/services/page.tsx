import type { Metadata } from 'next'
import { ServicesGrid } from '@/components/site/services-grid'
import { Integrations } from '@/components/site/integrations'
import { PerformanceMetrics } from '@/components/site/performance-metrics'

export const metadata: Metadata = {
  title: 'Services — Evershade',
  description: 'All 10 Evershade microservices with icons, descriptions, ports, and tier indicators.',
}

export default function ServicesPage() {
  return (
    <>
      <ServicesGrid />
      <Integrations />
      <PerformanceMetrics />
    </>
  )
}
