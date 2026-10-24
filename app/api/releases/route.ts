import { REPO_URL } from '@/lib/evershade'

const REPO_OWNER = 'LukaG712'
const REPO_NAME = 'Evershade'

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

function generateRss(releases: any[]): string {
  const items = releases
    .map((r) => {
      const date = new Date(r.published_at).toUTCString()
      const title = escapeXml(r.name || r.tag_name)
      const description = escapeXml(r.body || '')
      const link = r.html_url
      const guid = `https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/tag/${r.tag_name}`
      return `
    <item>
      <title>${title}</title>
      <link>${link}</link>
      <guid isPermaLink="false">${guid}</guid>
      <pubDate>${date}</pubDate>
      <description>${description}</description>
    </item>`
    })
    .join('')

  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escapeXml('Evershade Releases')}</title>
    <link>${REPO_URL}/releases</link>
    <description>${escapeXml('Latest releases and changelog for Evershade, a self-hosted AI agent platform.')}</description>
    <language>en-us</language>
    <generator>Evershade</generator>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="${REPO_URL}/releases" rel="self" />
${items}
  </channel>
</rss>`
}

export async function GET() {
  try {
    const res = await fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases?per_page=20`, {
      headers: {
        'User-Agent': 'EvershadePage',
      },
      next: { revalidate: 3600 },
    })

    if (!res.ok) {
      return new Response('Failed to fetch releases', { status: res.status })
    }

    const releases = await res.json()
    const rss = generateRss(releases)

    return new Response(rss, {
      headers: {
        'Content-Type': 'application/rss+xml; charset=utf-8',
        'Cache-Control': 'public, max-age=3600, s-maxage=3600',
      },
    })
  } catch {
    return new Response('Failed to generate feed', { status: 500 })
  }
}
