import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://evrshade.netlify.app'
  const sections = [
    '',
    '/#overview',
    '/#services',
    '/#console',
    '/#missions',
    '/#how-it-works',
    '/#trace',
    '/#architecture',
    '/#knowledge-graph',
    '/#project-layout',
    '/#platform',
    '/#harness',
    '/#security',
    '/#integrations',
    '/#slammer',
    '/#config-reference',
    '/#get-started',
    '/#download',
    '/#try-it',
    '/#docker-compose',
    '/#cli',
    '/#install',
    '/#use-cases',
    '/#about',
    '/#why',
    '/#metrics',
    '/#api',
    '/#glossary',
    '/#faq',
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
