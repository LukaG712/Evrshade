import { SectionHeading } from './section-heading'

const LAYOUT = [
  { path: 'greenie/', desc: 'Central orchestrator & API backend' },
  { path: 'slinker/', desc: 'Code execution engine' },
  { path: 'trapper/', desc: 'Web scraping & crawling' },
  { path: 'gobber/', desc: 'Persistent storage & knowledge graph' },
  { path: 'shrewd/', desc: 'LLM provider abstraction' },
  { path: 'sneaker/', desc: 'Metrics, traces, logs' },
  { path: 'hider/', desc: 'Encrypted secrets management' },
  { path: 'poltergeist/', desc: 'Notifications & async delivery' },
  { path: 'slammer/', desc: 'React web dashboard' },
  { path: 'speedy/', desc: 'The evershade CLI' },
  { path: 'docker-compose.yml', desc: 'Service orchestration' },
  { path: '.env.example', desc: 'Environment variable template' },
  { path: 'install.sh', desc: 'Installation script' },
  { path: 'start.sh', desc: 'Startup script' },
]

export function ProjectLayout() {
  return (
    <section id="project-layout" aria-labelledby="layout-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="layout-title"
        label="Project layout"
        title={
          <>
            Know the layout,
            <br />
            <span className="text-muted-foreground">quickly.</span>
          </>
        }
        lead="Each service lives in its own directory. The root contains the orchestration files."
      />

      <div className="mt-16 border border-foreground">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[500px] text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="py-4 pr-6 text-left font-mono text-[11px] uppercase tracking-wider">Path</th>
                <th className="py-4 px-4 text-left font-mono text-[11px] uppercase tracking-wider">Description</th>
              </tr>
            </thead>
            <tbody>
              {LAYOUT.map((item) => (
                <tr key={item.path} className="border-b border-border">
                  <td className="py-3 pr-6 font-mono text-sm">{item.path}</td>
                  <td className="py-3 px-4 text-muted-foreground">{item.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}
