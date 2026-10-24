import type { Metadata } from 'next'
import { Contributing } from '@/components/site/contributing'
import { Testimonials } from '@/components/site/testimonials'
import { Community } from '@/components/site/community'

export const metadata: Metadata = {
  title: 'Community — Evershade',
  description: 'Join the Evershade community. Contributing guide, testimonials, and how to get involved.',
}

export default function CommunityPage() {
  return (
    <>
      <Contributing />
      <Testimonials />
      <Community />
    </>
  )
}
