import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getPostData, getAllPostSlugs } from '@/lib/blog'
import { ArrowLeft } from 'lucide-react'

export function generateStaticParams() {
  return getAllPostSlugs().map((slug) => ({ slug }))
}

export default async function BlogPostPage({ params }: { params: { slug: string } }) {
  const post = await getPostData(params.slug)

  if (!post) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Hero */}
      <div className="relative border-b border-border pt-32 pb-16 px-4 md:pt-40 md:pb-20 md:px-[max(24px,3vw)]">
        <div className="absolute inset-0 bg-[length:32px_32px] bg-grid" aria-hidden="true" />
        <div className="relative">
          <Link
            href="/blog"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="size-4" />
            Back to blog
          </Link>
          <time className="mt-6 block font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
            {new Date(post.date).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </time>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight md:text-6xl">
            {post.title}
          </h1>
        </div>
      </div>

      {/* Content */}
      <article className="px-4 py-16 md:px-[max(24px,3vw)] md:py-20">
        <div
          className="prose prose-neutral max-w-3xl dark:prose-invert
            prose-h2:text-2xl prose-h2:font-semibold prose-h2:tracking-tight prose-h2:mt-12 prose-h2:mb-4
            prose-h3:text-xl prose-h3:font-semibold prose-h3:mt-8 prose-h3:mb-3
            prose-p:text-muted-foreground prose-p:leading-relaxed prose-p:text-pretty
            prose-li:text-muted-foreground prose-li:leading-relaxed
            prose-code:text-sm prose-code:bg-muted prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-sm
            prose-pre:bg-muted prose-pre:rounded-sm prose-pre:px-4 prose-pre:py-3
            prose-strong:text-foreground prose-strong:font-semibold
            prose-a:text-signal-ink prose-a:underline prose-a:decoration-signal/50 prose-a:decoration-1 prose-a:underline-offset-2
            prose-blockquote:border-l-2 prose-blockquote:border-signal prose-blockquote:text-muted-foreground
            prose-hr:border-border"
          dangerouslySetInnerHTML={{ __html: post.contentHtml }}
        />
      </article>

      {/* Bottom CTA */}
      <div className="px-4 pb-16 md:px-[max(24px,3vw)] md:pb-20">
        <div className="max-w-3xl border border-border p-8 text-center">
          <h2 className="text-xl font-semibold tracking-tight md:text-2xl">
            Enjoyed this post?<span className="text-signal">.</span>
          </h2>
          <p className="mt-3 text-muted-foreground">
            Check out more articles or try Evershade yourself.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <a
              href="/blog"
              className="inline-flex items-center gap-1.5 rounded-sm border border-foreground px-4 py-2 text-sm font-medium transition-colors hover:bg-foreground hover:text-background"
            >
              Back to blog
            </a>
            <a
              href="https://github.com/LukaG712/Evershade"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 rounded-sm border border-border px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:border-foreground/20 hover:text-foreground"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </div>

      {/* Spacer for mobile TOC */}
      <div className="h-20" />
    </div>
  )
}
