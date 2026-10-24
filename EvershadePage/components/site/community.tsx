import { ArrowUpRight, BookOpen, Code2, GitBranch, Heart, MessageCircle, Users } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const CONTRIBUTING_PATHS = [
  {
    icon: Code2,
    title: 'Good First Issues',
    description: 'Start here. Every issue is tagged with the service it belongs to and includes acceptance criteria.',
    link: 'https://github.com/LukaG712/Evershade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22',
    linkLabel: 'Browse issues',
  },
  {
    icon: BookOpen,
    title: 'Architecture Docs',
    description: 'Understand the system before you touch it. Service boundaries, data flow, and design decisions are documented.',
    link: `${REPO_URL}/tree/main/docs`,
    linkLabel: 'Read docs',
  },
  {
    icon: GitBranch,
    title: 'Plugin Registry',
    description: 'Build a custom skill, droid, or tool and publish it to the community registry. Plugins are self-contained and versioned.',
    link: `${REPO_URL}/tree/main/plugins`,
    linkLabel: 'Plugin template',
  },
  {
    icon: MessageCircle,
    title: 'Discussions',
    description: 'Propose ideas, ask questions, and share your Evershade setup. The community discusses features before they land.',
    link: `${REPO_URL}/discussions`,
    linkLabel: 'Join discussion',
  },
] as const

const STATS = [
  { label: 'Contributors', value: '40+' },
  { label: 'Plugins', value: '12' },
  { label: 'Languages', value: '8' },
  { label: 'Stars', value: '1.2k' },
] as const

export function Community() {
  return (
    <section id="community" aria-labelledby="community-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="community-title"
        index="18"
        label="Community"
        {
          /* eslint-disable react/jsx-one-expression-per-line */
          <>
            Build
            <span className="text-signal"> together.</span>
          </>
          /* eslint-enable react/jsx-one-expression-per-line */
        }
        lead="Evershade is open source and built by its community. Whether you fix a typo, add a skill, or contribute a new service — every pull request is welcome."
      />

      <div className="mt-16 grid gap-6 md:mt-24 md:grid-cols-2">
        {CONTRIBUTING_PATHS.map((path) => {
          const Icon = path.icon
          return (
            <a
              key={path.title}
              href={path.link}
              target="_blank"
              rel="noreferrer"
              className="group flex items-start gap-5 border border-border p-6 transition-colors hover:border-signal"
            >
              <span className="flex size-10 shrink-0 items-center justify-center border border-foreground/40 group-hover:border-signal">
                <Icon className="size-5 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
              </span>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-lg font-semibold tracking-tight">{path.title}</p>
                  <ArrowUpRight className="size-4 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
                </div>
                <p className="mt-1 text-sm leading-snug text-muted-foreground">{path.description}</p>
                <p className="mt-3 font-mono text-[10px] uppercase tracking-wider text-signal-ink">
                  {path.linkLabel}
                </p>
              </div>
            </a>
          )
        })}
      </div>

      <div className="mt-24 grid gap-8 border-t border-foreground pt-12 md:grid-cols-12">
        <div className="md:col-span-5">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'18.1 — By the numbers'}</p>
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {STATS.map((stat) => (
              <div key={stat.label} className="border border-border p-4">
                <p className="text-3xl font-semibold tracking-tight tabular-nums">{stat.value}</p>
                <p className="mt-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="md:col-span-5 md:col-start-7">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'18.2 — How to contribute'}</p>
          <ol className="mt-6 space-y-3 border-t border-foreground pt-6">
            {[
              'Fork the repository and clone it locally.',
              'Run <code>pnpm install</code> and <code>pnpm dev</code> to start the site.',
              'Create a feature branch from <code>main</code>.',
              'Open a pull request with a clear description and screenshots.',
            ].map((step, i) => (
              <li key={step} className="flex items-start gap-3">
                <span className="flex shrink-0 size-5 items-center justify-center rounded-full border border-foreground/40 font-mono text-[10px] tabular-nums">
                  {i + 1}
                </span>
                <p className="text-sm leading-snug text-muted-foreground" dangerouslySetInnerHTML={{ __html: step }} />
              </li>
            ))}
          </ol>
        </div>
      </div>

      <div className="mt-16 flex flex-col items-start gap-4 rounded border border-border bg-card p-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="flex items-center gap-2 text-lg font-semibold tracking-tight">
            <Heart className="size-5 text-signal" aria-hidden="true" />
            {'Love Evershade?'}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {'Star the repo, share it with a friend, or write about your setup.'}
          </p>
        </div>
        <a
          href={REPO_URL}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 border border-foreground px-4 py-2 font-mono text-[11px] uppercase tracking-wider transition-colors hover:bg-foreground hover:text-background"
        >
          <Users className="size-4" aria-hidden="true" />
          Star on GitHub
          <ArrowUpRight className="size-3.5" aria-hidden="true" />
        </a>
      </div>
    </section>
  )
}
