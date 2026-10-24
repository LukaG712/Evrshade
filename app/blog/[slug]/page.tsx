import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getPostData, getPostSlugs } from '@/lib/blog'

export async function generateStaticParams() {
  const slugs = getPostSlugs()
  return slugs.map((slug) => ({ slug: slug.replace(/\.md$/, '') }))
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await getPostData(slug)

  if (!post) {
    notFound()
  }

  return (
    <div className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <div className="max-w-3xl">
        <Link href="/blog" className="mb-8 inline-flex items-center gap-1 text-sm font-medium underline underline-offset-2 hover:text-signal-ink">
          ← Back to blog
        </Link>

        <time className="font-mono text-[11px] text-muted-foreground" dateTime={post.date}>
          {new Date(post.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
        </time>

        <h1 className="mt-2 text-balance text-4xl font-semibold leading-[0.9] tracking-[-0.05em] md:text-6xl lg:text-7xl">
          {post.title}
        </h1>

        <div
          className="prose prose-invert mt-8 max-w-none"
          dangerouslySetInnerHTML={{ __html: post.contentHtml }}
        />

        <div className="mt-16 border-t border-foreground pt-8">
          <Link href="/" className="text-sm font-medium underline underline-offset-2 hover:text-signal-ink">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  )
}
