export function SectionDivider({
  index,
  label,
  id,
}: {
  index: string
  label: string
  id: string
}) {
  return (
    <div id={id} className="px-4 pt-20 md:pt-32">
      <p className="font-mono text-sm font-bold uppercase tracking-wider text-signal-ink md:text-[11px]">{index}</p>
      <h2 className="mt-2 text-balance text-5xl font-semibold leading-[0.9] tracking-[-0.05em] md:text-7xl lg:text-9xl">
        {label}
      </h2>
    </div>
  )
}
