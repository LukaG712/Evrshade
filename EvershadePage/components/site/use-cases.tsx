import { Terminal, GitPullRequest, Search, Clock } from 'lucide-react'
import { SectionHeading } from './section-heading'

const USE_CASES = [
  {
    icon: GitPullRequest,
    title: 'Automate your code review pipeline',
    subtitle: 'From PR to production, safely',
    description: 'Connect Evershade to your GitHub repo. When a pull request opens, Greenie triggers a mission that reads the diff, runs tests in Slinker sandboxes, checks for security issues, and posts a structured review comment — all without your intervention.',
    steps: [
      'Push code or open a pull request',
      'GitHub webhook triggers a review mission',
      'Slinker runs tests in an isolated container',
      'Greenie posts the review with pass/fail summary',
    ],
    command: 'evershade trigger enable --type github --repo my-org/my-repo',
  },
  {
    icon: Search,
    title: 'Research and summarize a codebase',
    subtitle: 'Onboard faster, remember more',
    description: 'Point Evershade at a repository. Trapper crawls the docs, Gobber builds a knowledge graph with embeddings, and you can query it naturally — "how does authentication work?" or "where is the retry logic?" — getting answers with source references.',
    steps: [
      'Point Evershade at a repository URL',
      'Trapper crawls and extracts documentation',
      'Gobber indexes with hybrid search and graph links',
      'Query naturally via CLI or Slammer dashboard',
    ],
    command: 'evershade ingest --url https://github.com/my-org/my-repo',
  },
  {
    icon: Terminal,
    title: 'Build a feature from a spec',
    subtitle: 'Describe it, let Evershade build it',
    description: 'Write a mission spec — "add rate limiting to the API" — and Evershade plans the milestones, writes the code, runs the tests, fixes failures, and opens a pull request. You approve the sensitive steps and review the final diff.',
    steps: [
      'Write a mission spec in markdown or via CLI',
      'Shrewd plans milestones and features',
      'Workers execute in parallel Slinker sandboxes',
      'Fix-revalidate loop handles test failures automatically',
    ],
    command: 'evershade mission create --spec features/rate-limiting.md',
  },
  {
    icon: Clock,
    title: 'Run scheduled maintenance missions',
    subtitle: 'Set it and forget it, safely',
    description: 'Schedule recurring missions: dependency updates, log rotation, database vacuum, certificate checks. Evershade runs them on a schedule, notifies you via Slack or email when something needs attention, and stays quiet when everything is fine.',
    steps: [
      'Define a schedule with cron syntax',
      'Mission runs automatically at the scheduled time',
      'Poltergeist notifies only on failures or warnings',
      'Review results in Slammer or via CLI',
    ],
    command: 'evershade schedule add --cron "0 3 * * *" --task update-deps',
  },
] as const

export function UseCases() {
  return (
    <section id="use-cases" aria-labelledby="use-cases-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="use-cases-title"
        index="15"
        label="Use cases"
        title={
          <>
            What you do
            <br />
            <span className="text-muted-foreground">with Evershade.</span>
          </>
        }
        lead="Evershade isn't just a collection of services — it's a platform for automating the work that matters. Here are four concrete scenarios."
      />

      <div className="mt-16 md:mt-24">
        {USE_CASES.map((useCase, index) => {
          const Icon = useCase.icon
          return (
            <div
              key={useCase.title}
              className="grid gap-8 border-t border-foreground py-12 md:grid-cols-12 md:gap-8 md:py-16"
            >
              <div className="md:col-span-5">
                <div className="flex items-center gap-3">
                  <div className="flex size-10 items-center justify-center border border-foreground">
                    <Icon className="size-5 text-signal" aria-hidden="true" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-semibold tracking-tight md:text-3xl">{useCase.title}</h3>
                    <p className="font-mono text-xs text-muted-foreground">{useCase.subtitle}</p>
                  </div>
                </div>
                <p className="mt-4 text-pretty leading-snug text-muted-foreground">{useCase.description}</p>
                <div className="mt-6 rounded-md border border-border bg-foreground/[0.03] p-4">
                  <code className="font-mono text-xs text-signal">
                    <span className="text-muted-foreground">$ </span>
                    {useCase.command}
                  </code>
                </div>
              </div>
              <div className="md:col-span-5 md:col-start-8">
                <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">{'Flow'}</p>
                <ol className="mt-4 border-l border-border pl-6">
                  {useCase.steps.map((step, i) => (
                    <li key={i} className="relative pb-4 last:pb-0">
                      <span className="absolute -left-[29px] top-0 flex size-6 items-center justify-center rounded-full border border-foreground bg-background font-mono text-[10px] text-muted-foreground">
                        {String(i + 1).padStart(2, '0')}
                      </span>
                      <p className="text-sm leading-snug">{step}</p>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
