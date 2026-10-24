import type { Metadata } from 'next'
import { Security } from '@/components/site/security'
import { Harness } from '@/components/site/harness'

export const metadata: Metadata = {
  title: 'Security — Evershade Docs',
  description: 'How approval gates, the autonomy dial, encrypted secrets, and sandboxed execution keep your Evershade instance secure.',
}

export default function SecurityPage() {
  return (
    <>
      <Security />
      <Harness />
    </>
  )
}
