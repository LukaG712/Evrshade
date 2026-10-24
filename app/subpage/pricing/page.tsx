import type { Metadata } from 'next'
import { Pricing } from '@/components/site/pricing'

export const metadata: Metadata = {
  title: 'Pricing — Evershade',
  description: 'Evershade is free and open source. MIT License. Self-hosted. No telemetry, no credits, no vendor lock-in.',
}

export default function PricingPage() {
  return <Pricing />
}
