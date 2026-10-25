import type { Metadata } from 'next'
import { Contributing } from '@/components/site/contributing'
import { Community } from '@/components/site/community'

export const metadata: Metadata = {
  title: 'Community — Evershade',
  description: 'Join the Evershade community. Contributing guide and how to get involved.',
}

export default function CommunityPage() {
  return (
    <>
      <Contributing />
      <Community />
    </>
  )
}
