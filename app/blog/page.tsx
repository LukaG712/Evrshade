import Link from 'next/link'
import { getSortedPostsData } from '@/lib/blog'
import { ArrowLeft } from 'lucide-react'

export default function BlogPage() {
  const allPosts = getSortedPostsData()

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Hero */}
      <div className="relative border-b border-border pt-32 pb-16 px-4 md:pt-40 md:pb-20 md:px-[max(24px,3vw)]">
        <div className="absolute inset-0 bg-[length:32px_32px] bg-grid" aria-hidden="true" />
        <div className="relative">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="size-4" />
            Back to home
          </Link>
          <h1 className="mt-8 text-4xl font-semibold tracking-tight md:text-6xl">
            Blog<span className="text-signal">.</span>
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
            Engineering deep dives, tutorials, and announcements from the Evershade team.
          </p>
        </div>
      </div>

      {/* Posts list */}
      <div className="px-4 py-16 md:px-[max(24px,3vw)] md:py-20">
        <div className="max-w-3xl">
          {allPosts.map((post) => (
            <article
              key={post.slug}
              className="group border-t border-foreground py-8 first:pt-0 md:py-10"
            >
              <time className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                {new Date(post.date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </time>
              <Link
                href={`/blog/${post.slug}`}
                className="mt-2 block text-xl font-semibold tracking-tight transition-colors hover:text-signal-ink md:text-2xl"
              >
                {post.title}
              </Link>
              <p className="mt-3 text-pretty leading-relaxed text-muted-foreground">
                {post.excerpt}
              </p>
              <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors group-hover:text-foreground">
                Read more →
              </span>
            </article>
          ))}
        </div>
      </div>

      {/* Spacer for mobile TOC */}
      <div className="h-20" />
    </div>
  )
}
