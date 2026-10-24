import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://evershade.netlify.app'
  const sections = [
    '',
    '/#console',
    '/#missions',
    '/#trace',
    '/#harness',
    '/#security',
    '/#architecture',
    '/#integrations',
    '/#cli',
    '/#install',
    '/#changelog',
    '/#roadmap',
    '/#api',
    '/#why',
    '/#use-cases',
    '/#slammer',
    '/#knowledge-graph',
    '/#metrics',
    '/#community',
  ]

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 1,
    },
    ...sections.map((path) => ({
      url: `${baseUrl}${path}`,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: path === '' ? 1 : 0.7,
    })),
  ]
}
