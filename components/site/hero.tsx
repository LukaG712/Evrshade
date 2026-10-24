'use client'

import { useEffect, useRef } from 'react'
import { EDGES, LIVE_ACTIVITY, REPO_URL, SERVICES, TIER_LABEL, VERSION, type Service } from '@/lib/evershade'
import { useI18n } from '@/lib/i18n'
import { cn } from '@/lib/utils'
import { InstallDropdown } from './install-dropdown'
import { DownloadDropdown } from './download-dropdown'
import { StarCount } from './star-count'

const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v))
const range = (v: number, a: number, b: number) => clamp((v - a) / (b - a))
const lerp = (a: number, b: number, t: number) => a + (b - a) * t
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)

const DOT_SIZE: Record<Service['tier'], number> = {
  orchestrator: 22,
  core: 14,
  optional: 11,
  client: 11,
}

type Point = { x: number; y: number }

export function Hero() {
  const { t } = useI18n()
  const wrapRef = useRef<HTMLDivElement>(null)
  const stageRef = useRef<HTMLDivElement>(null)
  const headRef = useRef<HTMLHeadingElement>(null)
  const introRef = useRef<HTMLDivElement>(null)
  const hudRef = useRef<HTMLDivElement>(null)
  const titleRef = useRef<HTMLDivElement>(null)
  const barRef = useRef<HTMLDivElement>(null)
  const pctRef = useRef<HTMLSpanElement>(null)
  const nodeRefs = useRef<(HTMLDivElement | null)[]>([])
  const edgeRefs = useRef<(SVGLineElement | null)[]>([])
  const packetRefs = useRef<(SVGRectElement | null)[]>([])
  const edgeGroupRef = useRef<SVGGElement>(null)
  const liveRefs = useRef<(HTMLSpanElement | null)[]>([])

  useEffect(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const start = performance.now()
    let raf = 0
    let frameCount = 0
    let cachedRect: DOMRect | null = null
    let lastRectTop = Infinity

    const tick = (now: number) => {
      raf = requestAnimationFrame(tick)
      // Pause animation when tab is hidden to save main thread time
      if (document.hidden) return
      const wrap = wrapRef.current
      const stage = stageRef.current
      const head = headRef.current
      const title = titleRef.current
      if (!wrap || !stage || !head || !title) return

      // Only update DOM every 3rd frame to reduce main thread blocking
      frameCount++
      if (frameCount % 3 !== 0) return

      // Cache getBoundingClientRect - only re-read when scroll position changes significantly
      if (Math.abs(wrap.scrollTop - (cachedRect?.top ?? Infinity)) > 5 || !cachedRect) {
        cachedRect = wrap.getBoundingClientRect()
      }
      const rect = cachedRect!
      if (rect.bottom < 0) return
      // Skip if scroll position hasn't changed meaningfully
      if (Math.abs(rect.top - lastRectTop) < 1 && reduce) return
      lastRectTop = rect.top

      const W = stage.clientWidth
      const H = stage.clientHeight
      const desktop = W >= 768
      const pad = desktop ? Math.max(24, W * 0.03) : 16
      const time = reduce ? 0 : (now - start) / 1000
      const p = clamp(-rect.top / (wrap.offsetHeight - H))

      // Headline: oversized at the bottom → compact wordmark at top-left.
      const h = ease(range(p, 0, 0.42))
      const headW = head.offsetWidth
      const headH = head.offsetHeight
      const topY = desktop ? 96 : 76
      const finalScale = (desktop ? Math.min(W * 0.36, 560) : W * 0.64) / headW
      const s = lerp(1, finalScale, h)
      const ty = lerp(0, topY + headH * finalScale - (H - pad), h)
      head.style.transform = `translate3d(0, ${ty}px, 0) scale(${s})`
      stage.style.setProperty('--head-h', `${headH}px`)

      const fade = 1 - range(p, 0, 0.14)
      if (introRef.current) {
        introRef.current.style.opacity = String(fade)
        introRef.current.style.transform = `translate3d(0, ${(1 - fade) * -40}px, 0)`
      }
      if (hudRef.current) hudRef.current.style.opacity = String(fade)

      // Section title fades in alongside the modular grid.
      const tt = ease(range(p, 0.42, 0.62))
      const titleTop = desktop ? topY : topY + headH * finalScale + 16
      title.style.top = `${titleTop}px`
      title.style.opacity = String(tt)
      title.style.transform = `translate3d(0, ${(1 - tt) * 32}px, 0)`
      title.style.pointerEvents = tt > 0.5 ? 'auto' : 'none'

      if (barRef.current) barRef.current.style.transform = `scaleY(${p})`
      if (pctRef.current) pctRef.current.textContent = String(Math.round(p * 100)).padStart(3, '0')

      // Network layout (constellation around the orchestrator).
      const netTop = desktop ? 120 : 110
      const netBottom = H - pad - headH - (desktop ? 110 : 150)
      const cx = W / 2
      const cy = (netTop + netBottom) / 2
      const R = Math.max(60, Math.min((netBottom - netTop) / 2, W * (desktop ? 0.3 : 0.26)))
      const stretch = desktop ? 1.55 : 0.82
      const rot = reduce ? 0 : time * 0.06 * (1 - range(p, 0.2, 0.5))
      const breathe = reduce ? 0 : Math.sin(time * 0.8) * 3

      // Pre-compute trig values to avoid repeated Math calls
      const net: Point[] = new Point[SERVICES.length]
      for (let i = 0; i < SERVICES.length; i++) {
        const svc = SERVICES[i]
        if (svc.tier === 'orchestrator') net[i] = { x: cx, y: cy }
        else if (svc.tier === 'core') {
          const a = -Math.PI / 2 + (i - 1) * ((Math.PI * 2) / 3) + rot
          const r = R * 0.46 + breathe
          net[i] = { x: cx + Math.cos(a) * r * stretch, y: cy + Math.sin(a) * r }
        }
        else if (svc.tier === 'optional') {
          const a = Math.PI / 4 + (i - 4) * (Math.PI / 2) - rot * 0.7
          const r = R * 0.92 - breathe
          net[i] = { x: cx + Math.cos(a) * r * stretch, y: cy + Math.sin(a) * r }
        }
        else {
          const side = svc.id === 'slammer' ? -1 : 1
          const x = desktop ? cx + side * R * stretch * 1.45 : side < 0 ? pad + 12 : W - pad - 112
          net[i] = { x, y: desktop ? cy : cy + R * 1.05 }
        }
      }

      // Grid layout (modular service index).
      const cols = desktop ? 5 : 2
      const rows = SERVICES.length / cols
      const titleH = desktop ? 0 : title.offsetHeight + 16
      const gTop = desktop ? topY + headH * finalScale + 56 : titleTop + titleH
      const gBottom = H - pad
      const gW = W - pad * 2
      const cw = gW / cols
      const ch = Math.max(80, (gBottom - gTop) / rows)


      const centers: (Point | undefined)[] = new Array(SERVICES.length)
      for (let i = 0; i < SERVICES.length; i++) {
        const liveEl = liveRefs.current[i]
        if (liveEl) {
          const lines = LIVE_ACTIVITY[SERVICES[i].id] ?? []
          const k = lines.length ? Math.floor(time / 2.4 + i * 0.41) % lines.length : 0
          const txt = lines[k] ?? ''
          if (liveEl.textContent !== txt) liveEl.textContent = txt
        }
        const node = nodeRefs.current[i]
        if (!node) continue
        const g = ease(range(p, 0.22 + i * 0.018, 0.50 + i * 0.018))
        const col = i % cols
        const row = Math.floor(i / cols)
        const gx = pad + col * cw + cw / 2
        const gy = gTop + row * ch + ch / 2
        const x = lerp(net[i].x, gx, g)
        const y = lerp(net[i].y, gy, g)
        const dot = DOT_SIZE[SERVICES[i].tier]
        const w = lerp(dot, cw + 1, g)
        const hh = lerp(dot, ch + 1, g)
        centers[i] = { x, y }
        const style = node.style
        style.width = `${w}px`
        style.height = `${hh}px`
        style.transform = `translate3d(${x - w / 2}px, ${y - hh / 2}px, 0)`
        style.setProperty('--g', g.toFixed(3))
      }

      const edgeOpacity = 1 - range(p, 0.18, 0.42)
      if (edgeGroupRef.current) edgeGroupRef.current.style.opacity = String(edgeOpacity)
      if (edgeOpacity > 0) {
        EDGES.forEach(([a, b], i) => {
          const line = edgeRefs.current[i]
          const packet = packetRefs.current[i]
          const A = centers[a]
          const B = centers[b]
          if (!A || !B) return
          if (line) {
            line.setAttribute('x1', String(A.x))
            line.setAttribute('y1', String(A.y))
            line.setAttribute('x2', String(B.x))
            line.setAttribute('y2', String(B.y))
          }
          if (packet) {
            const f = (time * 0.32 + i * 0.137) % 1
            packet.setAttribute('x', String(lerp(A.x, B.x, f) - 2.5))
            packet.setAttribute('y', String(lerp(A.y, B.y, f) - 2.5))
            packet.style.opacity = String(reduce ? 0 : Math.sin(f * Math.PI))
          }
        })
      }
    }

    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  // On mobile (<768px), show a simplified static layout instead of the heavy scroll-driven animation
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 768

  if (isMobile) {
    return (
      <section id="hero-scroll" className="blueprint relative pb-10 pt-14 sm:pb-16 sm:pt-20">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-background/0 via-background/30 to-background/80" aria-hidden="true" />
        <div className="absolute inset-x-3 top-3 flex items-center justify-between font-mono text-[10px] uppercase tracking-wider text-muted-foreground sm:inset-x-4 sm:top-4 sm:text-[11px]">
          <span className="flex items-center gap-2">
            <span className="relative flex size-1.5">
              <span className="animate-pulse-ring absolute inset-0 bg-signal" />
              <span className="relative size-1.5 bg-signal" />
            </span>
            {`v${VERSION}`}
          </span>
          <span className="hidden sm:inline">{t('hero.tagline')}</span>
        </div>

        <div className="relative px-3 sm:px-4">
          <h1
            id="hero-title"
            className="font-semibold leading-[0.85] tracking-[-0.05em] text-foreground"
            style={{ fontSize: 'clamp(2.5rem, 16vw, 6rem)' }}
          >
            Evershade<span className="text-signal">.</span>
          </h1>

          <p className="mt-3 max-w-md text-pretty text-sm leading-snug sm:mt-4 sm:text-base">
            {t('hero.description')}
          </p>

          <div className="mt-4 flex flex-col gap-2.5">
            <InstallDropdown />
            <div className="flex flex-col gap-2.5 sm:flex-row sm:items-center">
              <DownloadDropdown />
              <a
                href={REPO_URL}
                target="_blank"
                rel="noreferrer"
                className="inline-flex h-11 flex-1 items-center justify-center gap-2 border border-foreground px-5 text-sm font-medium transition-colors hover:bg-foreground hover:text-background active:scale-[0.98]"
              >
                {t('hero.github')}
                <svg className="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg>
              </a>
            </div>
          </div>
          <div className="mt-3">
            <StarCount />
          </div>

          <div className="mt-6 border border-border p-4 sm:mt-8">
            <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">{t('hero.services-label')}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {SERVICES.filter(s => s.tier === 'orchestrator' || s.tier === 'core').map(svc => (
                <span
                  key={svc.id}
                  className="inline-flex items-center gap-1.5 border border-border px-2 py-1 font-mono text-[10px] text-muted-foreground"
                >
                  <span className={`size-1 ${svc.tier === 'orchestrator' ? 'bg-signal' : 'bg-foreground'}`} />
                  {svc.name}
                </span>
              ))}
              <span className="inline-flex items-center px-2 py-1 font-mono text-[10px] text-muted-foreground">
                +{SERVICES.filter(s => s.tier !== 'orchestrator' && s.tier !== 'core').length} {t('hero.more-services')}
              </span>
            </div>
          </div>

          <a
            href="#overview"
            className="mt-4 flex items-center gap-2 font-mono text-sm text-signal-ink underline underline-offset-4 sm:mt-8"
          >
            {t('hero.explore')}
          </a>
        </div>
      </section>
    )
  }

  return (
    <section ref={wrapRef} id="hero-scroll" aria-labelledby="hero-title" className="relative h-[300vh] md:h-[380vh]">
      <div ref={stageRef} className="blueprint sticky top-0 h-svh w-full overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-background/0 via-background/40 to-background/90" aria-hidden="true" />
        <CornerMarks />

        <div
          ref={hudRef}
          className="z-20 absolute inset-x-4 top-[72px] flex items-start justify-end sm:justify-between font-mono text-[11px] uppercase tracking-wider text-muted-foreground md:inset-x-[max(24px,3vw)]"
        >
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline">{t('hero.tagline')}</span>
            <StarCount />
          </div>
          <span className="flex items-center gap-2">
            <span className="relative flex size-1.5">
              <span className="animate-pulse-ring absolute inset-0 bg-signal" />
              <span className="relative size-1.5 bg-signal" />
            </span>
            {`v${VERSION}`}
          </span>
        </div>

        <svg className="pointer-events-none absolute inset-0 size-full" aria-hidden="true">
          <g ref={edgeGroupRef}>
            {EDGES.map((_, i) => (
              <line
                key={`edge-${i}`}
                ref={(el) => {
                  edgeRefs.current[i] = el
                }}
                stroke="currentColor"
                strokeOpacity={0.22}
                strokeWidth={1}
              />
            ))}
            {EDGES.map((_, i) => (
              <rect
                key={`packet-${i}`}
                ref={(el) => {
                  packetRefs.current[i] = el
                }}
                width={5}
                height={5}
                className="fill-signal"
              />
            ))}
          </g>
        </svg>

        <ul className="z-10" aria-label="Evershade services">
          {SERVICES.map((svc, i) => (
            <ServiceNode
              key={svc.id}
              svc={svc}
              index={i}
              nodeRef={(el) => {
                nodeRefs.current[i] = el
              }}
              liveRef={(el) => {
                liveRefs.current[i] = el
              }}
            />
          ))}
        </ul>

        <div
          ref={titleRef}
          className="z-15 absolute right-4 left-4 opacity-0 md:left-auto md:right-[max(24px,3vw)] md:w-[40%] md:max-w-xl"
        >
          <p className="font-mono text-[11px] uppercase tracking-wider text-signal-ink">{t('hero.modular-services')}</p>
          <p className="mt-3 text-pretty text-lg leading-snug tracking-tight md:text-2xl">
            {t('hero.modular-description')}
          </p>
        </div>

        <div
          ref={introRef}
          className="absolute inset-x-4 z-10 flex flex-col gap-5 md:inset-x-[max(24px,3vw)] md:flex-row md:items-end md:justify-between"
          style={{ bottom: 'calc(var(--head-h, 20vw) + max(16px, 3vw) + 24px)' }}
        >
          <p className="max-w-md text-pretty text-base leading-snug md:text-lg">
            {t('hero.description')}
          </p>
          <div className="flex items-center gap-2">
            <InstallDropdown />
            <DownloadDropdown />
            <a
              href={REPO_URL}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-11 items-center gap-2 border border-foreground px-5 text-sm font-medium transition-colors hover:bg-foreground hover:text-background focus-visible:outline-2 focus-visible:outline-offset-2"
            >
              {t('hero.github')}
              <svg className="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg>
            </a>
          </div>
        </div>

        <h1
          ref={headRef}
          id="hero-title"
          className="absolute left-4 bottom-4 origin-bottom-left font-semibold leading-[0.78] tracking-[-0.075em] will-change-transform md:left-[max(24px,3vw)] md:bottom-[max(24px,3vw)]"
          style={{ fontSize: 'clamp(4.5rem, 21.5vw, 26rem)' }}
        >
          Evershade<span className="text-signal">.</span>
        </h1>

        <div className="absolute top-1/2 right-2 hidden -translate-y-1/2 flex-col items-center gap-3 md:flex" aria-hidden="true">
          <div className="relative h-32 w-px bg-foreground/15">
            <div ref={barRef} className="absolute inset-0 origin-top scale-y-0 bg-signal" />
          </div>
          <span ref={pctRef} className="font-mono text-[10px] tabular-nums text-muted-foreground [writing-mode:vertical-rl]">
            000
          </span>
        </div>
      </div>
    </section>
  )
}

function ServiceNode({
  svc,
  index,
  nodeRef,
  liveRef,
}: {
  svc: Service
  index: number
  nodeRef: (el: HTMLDivElement | null) => void
  liveRef: (el: HTMLSpanElement | null) => void
}) {
  const filled = svc.tier === 'core'
  const orchestrator = svc.tier === 'orchestrator'

  return (
    <li>
      <div
        ref={nodeRef}
        className="absolute top-0 left-0 size-0 will-change-transform"
        style={{ '--g': 0 } as React.CSSProperties}
      >
        <div
          className={cn(
            'absolute inset-0 border bg-background',
            svc.tier === 'client' ? 'border-dashed border-foreground/60' : 'border-foreground',
          )}
        />
        <div
          className={cn('absolute inset-0', orchestrator ? 'bg-signal' : filled ? 'bg-foreground' : 'bg-transparent')}
          style={{ opacity: 'max(0, 1 - var(--g) * 4)' }}
        />
        {orchestrator ? (
          <span
            className="animate-pulse-ring absolute inset-0 border border-signal"
            style={{ opacity: 'calc(1 - var(--g))' }}
            aria-hidden="true"
          />
        ) : null}

        <span
          className="pointer-events-none absolute top-1/2 left-[calc(100%+10px)] -translate-y-1/2 whitespace-nowrap font-mono text-[10px] uppercase tracking-wider"
          style={{ opacity: 'max(0, 1 - var(--g) * 4)' }}
        >
          {svc.name}
          <span className="text-muted-foreground">{svc.port === 'CLI' ? ' cli' : ` :${svc.port}`}</span>
        </span>

        <div
          className="absolute inset-0 flex flex-col justify-between overflow-hidden p-3 md:p-5"
          style={{ opacity: 'max(0, var(--g) * 3 - 2)' }}
        >
          <div className="flex items-start justify-between font-mono text-[10px] uppercase tracking-wider text-muted-foreground md:text-[11px]">
            <span className="flex items-center gap-1.5">
              <span
                className={cn(
                  'size-1.5',
                  orchestrator ? 'bg-signal' : filled ? 'bg-foreground' : 'border border-foreground',
                )}
              />
              {String(index + 1).padStart(2, '0')}
              <span className="hidden lg:inline">{` / ${TIER_LABEL[svc.tier]}`}</span>
            </span>
            <span className="tabular-nums">{svc.port === 'CLI' ? 'CLI' : `:${svc.port}`}</span>
          </div>
          <div>
            <p className="text-xl font-semibold leading-none tracking-tight md:text-3xl">{svc.name}</p>
            <p className="mt-2 hidden text-sm leading-snug text-muted-foreground md:block">{svc.role}</p>
            <p
              className="mt-2 flex items-center gap-1.5 font-mono text-[10px] text-signal-ink md:mt-3 md:text-[11px]"
              style={{ opacity: 'var(--l, 0)' }}
            >
              <span className="size-1 shrink-0 animate-pulse bg-signal" aria-hidden="true" />
              <span ref={liveRef} className="truncate" />
            </p>
          </div>
        </div>
        <div
          className="pointer-events-none absolute inset-x-0 bottom-0 h-0.5 overflow-hidden"
          style={{ opacity: 'var(--l, 0)' }}
          aria-hidden="true"
        >
          <div
            className="h-full w-1/3 bg-signal"
            style={{ animation: `scan ${2 + (index % 4) * 0.45}s ease-in-out ${index * 0.17}s infinite` }}
          />
        </div>
      </div>
    </li>
  )
}

function CornerMarks() {
  const base = 'pointer-events-none absolute size-3 border-foreground/40'
  return (
    <div aria-hidden="true">
      <span className={cn(base, 'top-[60px] left-2 border-t border-l')} />
      <span className={cn(base, 'top-[60px] right-2 border-t border-r')} />
      <span className={cn(base, 'bottom-2 left-2 border-b border-l')} />
      <span className={cn(base, 'bottom-2 right-2 border-b border-r')} />
    </div>
  )
}
