import { NextResponse } from 'next/server'

const REPO_OWNER = 'LukaG712'
const REPO_NAME = 'Evershade'

export const revalidate = 3600 // Cache for 1 hour

export async function GET() {
  try {
    const res = await fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases?per_page=10`, {
      headers: {
        'User-Agent': 'EvershadePage',
        'Accept': 'application/vnd.github+json',
      },
      next: { revalidate },
    })

    if (!res.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch releases' },
        { status: res.status }
      )
    }

    const releases = await res.json()

    // Transform to a cleaner format
    const data = releases.map((r: any) => ({
      tag: r.tag_name,
      name: r.name || r.tag_name,
      publishedAt: r.published_at,
      body: r.body || '',
      url: r.html_url,
    }))

    return NextResponse.json(data)
  } catch {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
