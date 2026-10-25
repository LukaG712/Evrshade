import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://evrshade.netlify.app'
  const sections = [
    '',
    '/#overview',
    '/#console',
    '/#missions',
    '/#how-it-works',
    '/#trace',
    '/#architecture',
    '/#knowledge-graph',
    '/#platform',
    '/#security',
    '/#integrations',
    '/#slammer',
    '/#get-started',
    '/#cli',
    '/#install',
    '/#use-cases',
    '/#about',
    '/#why',
    '/#metrics',
    '/#api',
    '/#roadmap',
    '/#changelog',
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
