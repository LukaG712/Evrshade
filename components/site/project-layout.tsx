import { FolderTree } from 'lucide-react'
import { SectionHeading } from './section-heading'

const TREE = [
  { name: 'evershade/', type: 'dir' },
  { name: '  services/', type: 'dir', desc: 'All 10 microservices' },
  { name: '    greenie/', type: 'file', desc: 'Orchestrator & API' },
  { name: '    slinker/', type: 'file', desc: 'Code execution' },
  { name: '    trapper/', type: 'file', desc: 'Web scraping' },
  { name: '    gobber/', type: 'file', desc: 'Knowledge graph' },
  { name: '    shrewd/', type: 'file', desc: 'LLM abstraction' },
  { name: '    sneaker/', type: 'file', desc: 'Observability' },
  { name: '    hider/', type: 'file', desc: 'Secrets management' },
  { name: '    poltergeist/', type: 'file', desc: 'Notifications' },
  { name: '    slammer/', type: 'file', desc: 'React dashboard' },
  { name: '    speedy/', type: 'file', desc: 'CLI tool' },
  { name: '  compose/', type: 'dir', desc: 'Docker Compose configs' },
  { name: '    docker-compose.yml', type: 'file', desc: 'Main compose file' },
  { name: '    profiles/', type: 'dir', desc: 'Profile overrides' },
  { name: '  docs/', type: 'dir', desc: 'Documentation' },
  { name: '    ARCHITECTURE.md', type: 'file', desc: 'System design' },
  { name: '    ROADMAP.md', type: 'file', desc: 'Development plan' },
  { name: '    CHANGELOG.md', type: 'file', desc: 'Release history' },
  { name: '  .env.example', type: 'file', desc: 'Environment template' },
  { name: '  version-manifest.json', type: 'file', desc: 'Service versions' },
] as const

export function ProjectLayout() {
  return (
    <section id="project-layout" aria-labelledby="project-layout-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="project-layout-title"
        label="Project"
        title={
          <>Know the layout<span className="text-signal">.</span></>
        }
        lead="Every service lives in its own directory under services/. Compose configs and docs are at the root."
      />

      <div className="mt-16 grid gap-6 md:grid-cols-12 md:mt-24">
        <div className="md:col-span-7">
          <div className="overflow-auto rounded border border-border bg-background p-4">
            <div className="flex items-center gap-2 mb-3">
              <FolderTree className="size-4 text-signal-ink" aria-hidden="true" />
              <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Directory structure'}</p>
            </div>
            <ul className="font-mono text-xs leading-relaxed">
              {TREE.map((item, i) => (
                <li key={i} className="flex items-start gap-3 py-0.5">
                  <span className="shrink-0 w-24 truncate text-foreground">{item.name}</span>
                  {item.desc && (
                    <span className="text-muted-foreground">{item.desc}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="md:col-span-5">
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{'Key directories'}</p>
          <dl className="mt-6 space-y-4 border-t border-foreground pt-6">
            {[
              { name: 'services/', desc: 'Each subdirectory is a standalone microservice with its own Dockerfile, dependencies, and source code.' },
              { name: 'compose/', desc: 'Docker Compose files and profile overrides. The main compose file references all services.' },
              { name: 'docs/', desc: 'Architecture documentation, roadmap, changelog, and contributing guidelines.' },
              { name: '.env.example', desc: 'Template for environment variables. Copy to .env and fill in your values before starting.' },
              { name: 'version-manifest.json', desc: 'Tracks the current version of every service. Used for dependency resolution and health checks.' },
            ].map((item) => (
              <div key={item.name}>
                <dt className="font-mono text-sm font-semibold tracking-tight">{item.name}</dt>
                <dd className="mt-1 text-sm leading-snug text-muted-foreground">{item.desc}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  )
}
