import Link from 'next/link'
import { getAllPosts } from '@/lib/blog'

export default function BlogPage() {
  const posts = getAllPosts()

  return (
    <div className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">Blog</p>
      <h1 className="mt-2 text-balance text-5xl font-semibold leading-[0.9] tracking-[-0.05em] md:text-7xl lg:text-9xl">
        Engineering<span className="text-signal">.</span>
      </h1>
      <p className="mt-6 max-w-2xl text-pretty text-lg leading-snug text-muted-foreground">
        Architecture deep dives, tutorials, and announcements from the Evershade team.
      </p>

      <div className="mt-16 space-y-4">
        {posts.map((post) => (
          <Link
            key={post.slug}
            href={`/blog/${post.slug}`}
            className="block border border-foreground p-5 transition-colors hover:bg-muted/50"
          >
            <div className="flex items-center gap-3">
              <time className="font-mono text-[11px] text-muted-foreground" dateTime={post.date}>
                {new Date(post.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
              </time>
            </div>
            <h2 className="mt-2 text-xl font-semibold tracking-tight">{post.title}</h2>
            <p className="mt-1 text-sm leading-snug text-muted-foreground">{post.excerpt}</p>
          </Link>
        ))}
      </div>

      <div className="mt-16 border-t border-foreground pt-8">
        <p className="text-sm text-muted-foreground">Back to the main site</p>
        <Link href="/" className="mt-2 inline-flex items-center gap-1 text-sm font-medium underline underline-offset-2 hover:text-signal-ink">
          ← Home
        </Link>
      </div>
    </div>
  )
}
