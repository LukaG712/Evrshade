import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { getAllPosts } from '@/lib/blog'

export function RelatedPosts({ currentSlug }: { currentSlug: string }) {
  const allPosts = getAllPosts()
  const related = allPosts
    .filter((post) => post.slug !== currentSlug)
    .slice(0, 3)

  if (related.length === 0) return null

  return (
    <div className="mt-16 border-t border-foreground pt-8">
      <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
        Related posts
      </p>
      <ul className="mt-4 space-y-3">
        {related.map((post) => (
          <li key={post.slug}>
            <Link
              href={`/blog/${post.slug}`}
              className="group flex items-center justify-between text-sm font-medium underline underline-offset-2 hover:text-signal-ink"
            >
              <span>
                <time className="mr-2 font-mono text-[11px] text-muted-foreground" dateTime={post.date}>
                  {new Date(post.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </time>
                {post.title}
              </span>
              <ArrowRight className="ml-2 size-4 shrink-0 opacity-0 transition-opacity group-hover:opacity-100" aria-hidden="true" />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
