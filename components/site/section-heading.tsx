export function SectionHeading({
  label,
  title,
  lead,
  id,
}: {
  label: string
  title: React.ReactNode
  lead?: React.ReactNode
  id: string
}) {
  return (
    <div className="grid gap-6 border-t border-foreground pt-6 md:grid-cols-12 md:gap-8">
      <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground md:col-span-3">{label}</p>
      <div className="md:col-span-9">
        <h3 id={id} className="text-balance text-2xl font-semibold leading-[0.9] tracking-[-0.05em] md:text-5xl lg:text-7xl">
          {title}
        </h3>
        {lead ? <p className="mt-4 max-w-2xl text-pretty text-base leading-snug text-muted-foreground md:mt-6 md:text-xl">{lead}</p> : null}
      </div>
    </div>
  )
}
