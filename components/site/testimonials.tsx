import { SectionHeading } from './section-heading'

const TESTIMONIALS = [
  {
    quote: 'Evershade replaced three separate tools for me. One docker-compose up and everything just works.',
    author: 'Self-hosted developer',
    role: 'Full-stack engineer',
  },
  {
    quote: 'The approval gates give me confidence to let agents work autonomously without worrying about side effects.',
    author: 'DevOps engineer',
    role: 'Infrastructure lead',
  },
  {
    quote: 'We switched from a cloud AI platform to Evershade. Our data stays on our servers, and the cost dropped to zero.',
    author: 'Startup CTO',
    role: 'Founder & CEO',
  },
  {
    quote: 'The knowledge graph is a game-changer. Gobber remembers context across sessions in a way no other tool does.',
    author: 'AI researcher',
    role: 'ML engineer',
  },
  {
    quote: 'I contributed a plugin in my first week. The modular architecture makes it easy to extend anything.',
    author: 'Open source contributor',
    role: 'Backend developer',
  },
  {
    quote: 'The observability built into Sneaker saved me hours of debugging. Metrics, traces, and logs in one place.',
    author: 'Platform engineer',
    role: 'SRE',
  },
]

export function Testimonials() {
  return (
    <section id="testimonials" aria-labelledby="testimonials-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
      <SectionHeading
        id="testimonials-title"
        label="Testimonials"
        title={
          <>
            Loved by,
            <br />
            <span className="text-muted-foreground">self-hosted developers.</span>
          </>
        }
      />

      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {TESTIMONIALS.map((t) => (
          <blockquote key={t.author} className="border border-foreground p-5">
            <p className="text-sm leading-snug italic text-muted-foreground">"{t.quote}"</p>
            <footer className="mt-4">
              <p className="text-sm font-semibold tracking-tight">{t.author}</p>
              <p className="text-xs text-muted-foreground">{t.role}</p>
            </footer>
          </blockquote>
        ))}
      </div>
    </section>
  )
}
