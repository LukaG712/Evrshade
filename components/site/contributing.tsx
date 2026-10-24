import { ArrowUpRight, BookOpen, Bug, Code2, Container, GitBranch, Terminal, Zap } from 'lucide-react'
import { REPO_URL } from '@/lib/evershade'
import { SectionHeading } from './section-heading'

const STEPS = [
  {
    icon: GitBranch,
    title: 'Fork & clone',
    description: 'Fork the Evershade repository, clone it locally, and create a feature branch from main.',
    code: 'git clone https://github.com/YOUR-USERNAME/Evershade.git',
  },
  {
    icon: Terminal,
    title: 'Set up the environment',
    description: 'Install dependencies and verify everything is working with the dev server.',
    code: 'pnpm install && pnpm dev',
  },
  {
    icon: Container,
    title: 'Run the services',
    description: 'Start the full stack with Docker Compose to test your changes against all services.',
    code: 'docker compose --profile full up -d',
  },
  {
    icon: Code2,
    title: 'Make your changes',
    description: 'Follow the existing code style. Add tests for new logic. Update docs if you change an API.',
    code: 'pnpm build && pnpm test',
  },
  {
    icon: Zap,
    title: 'Open a pull request',
    description: 'Describe what you changed, why, and include screenshots for UI changes. Link any related issues.',
    code: 'git push origin your-branch',
  },
] as const

const AREAS = [
  {
    icon: Bug,
    title: 'Bug fixes',
    description: 'Fix a failing test, patch a security issue, or correct documentation. Every fix matters.',
    link: 'https://github.com/LukaG712/Evershade/issues?q=is%3Aissue+is%3Aopen+label%3Abug',
    linkLabel: 'Browse bugs',
  },
  {
    icon: Code2,
    title: 'Good first issues',
    description: 'Tagged issues perfect for new contributors. Each includes acceptance criteria and the service it belongs to.',
    link: 'https://github.com/LukaG712/Evershade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22',
    linkLabel: 'Start here',
  },
  {
    icon: BookOpen,
    title: 'Documentation',
    description: 'Improve README files, add examples, write guides, or clarify confusing sections.',
    link: `${REPO_URL}/tree/master/docs`,
    linkLabel: 'View docs',
  },
  {
    icon: Container,
    title: 'Plugins & skills',
    description: 'Build a custom skill, droid, or tool and publish it. Plugins are self-contained and versioned.',
    link: `${REPO_URL}/tree/master/docs/DEVELOPMENT.md`,
    linkLabel: 'Plugin guide',
  },
] as const

export function Contributing() {
  return (
    <section id="contributing" aria-labelledby="contributing-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="contributing-title"
        label="Contributing"
        title={<>Ship code<span className="text-signal">.</span></>}
        lead="From fixing a typo to adding a new service — every contribution is welcome. Here's how to get started and make your first pull request."
      />

      {/* Steps */}
      <div className="mt-12 stagger space-y-0 md:mt-16 md:grid md:grid-cols-5 md:gap-6">
        {STEPS.map((step, i) => {
          const Icon = step.icon
          return (
            <div key={step.title} className="group border-t border-foreground pt-6 md:border-t-0 md:border md:border-border md:pt-0 md:hover:border-signal">
              <div className="md:p-5">
                <div className="flex items-center gap-2">
                  <span className="flex size-8 items-center justify-center border border-foreground/40 font-mono text-[10px] text-muted-foreground group-hover:border-signal">
                    <Icon className="size-4" aria-hidden="true" />
                  </span>
                  <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                    Step {i + 1}
                  </span>
                </div>
                <p className="mt-3 font-semibold tracking-tight">{step.title}</p>
                <p className="mt-1 text-sm leading-snug text-muted-foreground">{step.description}</p>
                <div className="mt-3 overflow-x-auto">
                  <code className="block rounded bg-muted px-2 py-1.5 font-mono text-[11px]">{step.code}</code>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Contributing areas */}
      <div className="mt-16 stagger grid gap-4 md:mt-24 md:grid-cols-2">
        {AREAS.map((area) => {
          const Icon = area.icon
          return (
            <a
              key={area.title}
              href={area.link}
              target="_blank"
              rel="noreferrer"
              className="group flex items-start gap-5 border border-border p-6 transition-colors hover:border-signal"
            >
              <span className="flex size-10 shrink-0 items-center justify-center border border-foreground/40 group-hover:border-signal">
                <Icon className="size-5 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
              </span>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-lg font-semibold tracking-tight">{area.title}</p>
                  <ArrowUpRight className="size-4 text-muted-foreground group-hover:text-signal-ink" aria-hidden="true" />
                </div>
                <p className="mt-1 text-sm leading-snug text-muted-foreground">{area.description}</p>
                <p className="mt-3 font-mono text-[10px] uppercase tracking-wider text-signal-ink">
                  {area.linkLabel}
                </p>
              </div>
            </a>
          )
        })}
      </div>
    </section>
  )
}
