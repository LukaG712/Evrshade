import { ArrowUpRight, BookOpen, Bug, Code2, GitBranch, Terminal } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const STEPS = [
  { icon: GitBranch, title: 'Fork the repo', body: 'Fork Evershade on GitHub and clone your fork locally.' },
  { icon: Terminal, title: 'Set up', body: 'Run the install script with the minimal profile to get the dev environment ready.' },
  { icon: Code2, title: 'Code', body: 'Make your changes in a feature branch. Follow the existing code style.' },
  { icon: Bug, title: 'Test', body: 'Run the test suite and ensure all checks pass before submitting.' },
  { icon: GitBranch, title: 'Pull request', body: 'Open a PR against master. Maintainers will review and merge.' },
]

const AREAS = [
  { title: 'Bug fixes', link: `${REPO_URL}/issues?q=is%3Aissue+is%3Aopen+label%3Abug`, label: 'Open bugs' },
  { title: 'Good first issues', link: `${REPO_URL}/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22`, label: 'Explore' },
  { title: 'Documentation', link: `${REPO_URL}/tree/master/docs`, label: 'Docs folder' },
  { title: 'Plugins', link: `${REPO_URL}/tree/master/plugins`, label: 'Plugin registry' },
]

export function Contributing() {
  return (
    <section id="contributing" aria-labelledby="contributing-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="contributing-title"
        label="Contributing"
        title={
          <>
            Build together,
            <br />
            <span className="text-muted-foreground">fork nothing.</span>
          </>
        }
        lead="Evershade is open source and built by its community. Every pull request is welcome."
      />

      <div className="mt-16 grid gap-8 md:grid-cols-5">
        {STEPS.map((step, i) => {
          const Icon = step.icon
          return (
            <div key={step.title} className="border-t border-foreground pt-6">
              <Icon className="size-5 text-muted-foreground" aria-hidden="true" />
              <p className="mt-4 font-mono text-[11px] text-muted-foreground">Step {i + 1}</p>
              <p className="mt-2 text-lg font-semibold tracking-tight">{step.title}</p>
              <p className="mt-1 text-sm leading-snug text-muted-foreground">{step.body}</p>
            </div>
          )
        })}
      </div>

      <div className="mt-16 grid gap-4 sm:grid-cols-2 md:grid-cols-4">
        {AREAS.map((area) => (
          <a
            key={area.title}
            href={area.link}
            target="_blank"
            rel="noreferrer"
            className="group flex items-center justify-between border border-foreground p-5 transition-colors hover:bg-muted/50"
          >
            <span className="font-semibold tracking-tight">{area.title}</span>
            <ArrowUpRight className="size-4 opacity-40 transition-opacity group-hover:opacity-100" aria-hidden="true" />
          </a>
        ))}
      </div>
    </section>
  )
}
