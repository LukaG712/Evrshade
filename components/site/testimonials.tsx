import { MessageCircle, Quote } from 'lucide-react'
import { SectionHeading } from './section-heading'

const TESTIMONIALS = [
  {
    quote: 'Evershade lets me run AI agents on my own machine without worrying about data leaving my network. The modular design means I only run what I need.',
    author: 'Self-hosted developer',
    role: 'Early adopter',
  },
  {
    quote: 'The approval gates give me confidence to let agents work autonomously. I can step in when it matters and stay out of the way when it doesn\'t.',
    author: 'DevOps engineer',
    role: 'Beta tester',
  },
  {
    quote: 'Switching from a cloud AI platform to Evershade saved us money and gave us full control. The Docker Compose setup made migration straightforward.',
    author: 'Startup CTO',
    role: 'Community member',
  },
  {
    quote: 'The knowledge graph in Gobber is a game changer. My agents actually remember context across sessions instead of starting from scratch every time.',
    author: 'Full-stack developer',
    role: 'Contributor',
  },
  {
    quote: 'I love that I can dial the autonomy up or down. Supervised mode for production, full autonomous for experiments — all on the same setup.',
    author: 'AI researcher',
    role: 'Discord member',
  },
  {
    quote: 'The Slammer dashboard gives me everything I need to monitor missions in real time. SSE streaming makes it feel like watching a build live.',
    author: 'Backend engineer',
    role: 'Early adopter',
  },
] as const

export function Testimonials() {
  return (
    <section id="testimonials" aria-labelledby="testimonials-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="testimonials-title"
        label="Testimonials"
        title={<>People use it<span className="text-signal">.</span></>}
        lead="Early adopters, beta testers, and community members share why they chose Evershade for their self-hosted AI workflow."
      />

      <div className="mt-12 stagger grid gap-4 sm:grid-cols-2 lg:grid-cols-3 md:mt-16">
        {TESTIMONIALS.map((t) => (
          <div
            key={t.quote}
            className="relative border border-border p-6"
          >
            <Quote className="absolute right-4 top-4 size-5 text-muted-foreground/20" aria-hidden="true" />
            <p className="relative text-sm leading-snug text-muted-foreground italic">
              "{t.quote}"
            </p>
            <div className="mt-4 flex items-center gap-2">
              <span className="flex size-8 items-center justify-center rounded-full border border-border bg-muted text-xs font-medium">
                <MessageCircle className="size-4 text-muted-foreground" aria-hidden="true" />
              </span>
              <div>
                <p className="text-sm font-semibold tracking-tight">{t.author}</p>
                <p className="text-xs text-muted-foreground">{t.role}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
