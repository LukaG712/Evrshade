import { NextResponse } from 'next/server'

const REPO_OWNER = 'LukaG712'
const REPO_NAME = 'Evershade'

export const revalidate = 3600 // Cache for 1 hour

export async function GET() {
  try {
    const [repoRes, contributorsRes] = await Promise.all([
      fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`, {
        headers: { 'User-Agent': 'EvershadePage' },
      }),
      fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contributors?per_page=1`, {
        headers: {
          'User-Agent': 'EvershadePage',
          'Accept': 'application/vnd.github+json',
        },
      }),
    ])

    if (!repoRes.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch GitHub data' },
        { status: repoRes.status }
      )
    }

    const repo = await repoRes.json()

    // Get total contributor count from Link header
    let contributors = 0
    if (contributorsRes.ok) {
      const linkHeader = contributorsRes.headers.get('link')
      if (linkHeader) {
        const match = linkHeader.match(/&page=(\d+)>; rel="last"/)
        if (match) contributors = parseInt(match[1], 10)
      }
      // Fallback: if no Link header, at least 1 contributor exists
      if (contributors === 0) contributors = 1
    }

    return NextResponse.json({
      stars: repo.stargazers_count,
      forks: repo.forks_count,
      contributors,
      openIssues: repo.open_issues_count,
      watchers: repo.watchers_count,
      size: repo.size, // KB
      created: repo.created_at,
      updated: repo.updated_at,
      license: repo.license?.spdx_id,
      language: repo.language,
      topics: repo.topics,
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}