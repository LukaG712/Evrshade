# Evershade Site (Internal)

> Private marketing & documentation site for [Evershade](https://github.com/LukaG712/Evershade).
> Deployed at **https://evrshade.netlify.app**

---

## Quick Start

```powershell
pnpm install
pnpm dev        # http://localhost:3000
pnpm build      # production build
pnpm start      # serve production build
```

- **Package manager:** pnpm@12.3.4
- **Node:** ^18 (Next.js 16 minimum)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 16.4.0 (App Router, Turbopack) |
| Runtime | React 19 |
| Styling | Tailwind CSS v4 + tw-animate-css |
| UI | shadcn/ui + shadcn 4.11.0 + class-variance-authority + tailwind-merge |
| Icons | lucide-react |
| Analytics | @vercel/analytics |
| Language | TypeScript 5.7.3 |
| Deployment | Netlify (edge functions for API routes) |

---

## Project Structure

```
app/
├── layout.tsx          # Root layout, SEO, fonts, theme provider
├── page.tsx            # Homepage (~30 sections, all components)
├── globals.css         # Tailwind v4, custom properties, animations
├── robots.ts           # Dynamic robots.txt
├── sitemap.ts          # Dynamic sitemap
├── api/
│   ├── dashboard/route.ts      # Mock dashboard data (JSON)
│   ├── github-stats/route.ts   # Live GitHub repo stats (1h ISR cache)
│   ├── releases-json/route.ts  # Live GitHub releases (1h ISR cache)
│   └── releases/route.ts       # Redirect to releases-json
└── subpage/
    ├── layout.tsx              # Subpage wrapper layout
    ├── changelog/page.tsx
    ├── community/page.tsx
    ├── compare/page.tsx        # Only shows migration guide
    ├── pricing/page.tsx
    ├── services/page.tsx
    └── docs/
        ├── install/page.tsx
        ├── configuration/page.tsx
        ├── architecture/page.tsx
        └── security/page.tsx

components/site/
├── header.tsx              # Transparent header, scroll-aware, context-aware nav
├── hero.tsx                # Scroll-driven animation (380vh), service network→grid
├── slammer-preview.tsx     # Interactive dashboard with real-time simulated data
├── mission-console.tsx     # Simulated mission replay (not a real service)
├── performance-metrics.tsx # Design goals, mission lifecycle, factory attribution
├── api-reference.tsx       # Collapsible API endpoints table
├── knowledge-graph.tsx     # Gobber query pipeline (collapsible)
├── install.tsx             # Quickstart guide, .env variables
├── community.tsx           # Contributing paths + steps (merged section)
├── changelog-ticker.tsx    # Live GitHub releases
├── roadmap.tsx             # Shipped / In progress / Planned
├── faq.tsx                 # FAQ accordion
├── known-limitations.tsx   # Beta limitations
├── system-requirements.tsx # Hardware/software requirements
├── security.tsx            # Security defaults section
├── footer.tsx              # Footer with links
├── theme-toggle.tsx        # Dark/light mode toggle
├── reading-progress.tsx    # Scroll progress bar
├── back-to-top.tsx         # Back-to-top floating button
├── swipe-navigation.tsx    # Mobile horizontal swipe between sections
├── haptic-feedback.tsx     # Mobile haptic feedback
├── mobile-toc.tsx          # Mobile table of contents
├── section-reveal.tsx      # Scroll-triggered section animations
├── section-divider.tsx     # Section separators
├── cli.tsx                 # Animated CLI demo
├── glossary.tsx            # Term definitions
├── project-layout.tsx      # Project directory tree
├── request-trace.tsx       # Request flow diagram
├── services-grid.tsx       # All services overview
├── integrations.tsx        # Integration cards
├── architecture.tsx        # Architecture diagram
├── config-reference.tsx    # Config file reference
├── contributing.tsx        # Contributing guide
├── contributor-avatars.tsx # GitHub contributor avatars
├── counter.tsx             # Animated counter
├── discord-widget.tsx      # Discord server widget
├── docker-compose.tsx      # Docker Compose example
├── download-dropdown.tsx   # Download platform selector
├── build-status.tsx        # CI build status badge
├── blog-toc.tsx            # Blog table of contents
├── comparison.tsx          # DEAD CODE — not used, keep deleted
└── harness.tsx             # Test harness component

lib/
├── evershade.ts            # Service definitions, versions, roadmap data
├── dashboard.ts            # Dashboard types and mock data generator
└── mission-script.ts       # Mission replay script data

public/
└── og.png                  # Open Graph / Twitter card image

.github/workflows/
└── nextjs.yml              # GitHub Actions CI (build + lint)
```

---

## Key Components

### Homepage (`app/page.tsx`)
The homepage is a long-scrolling single page with ~30 sections. Order matters for the hero scroll animation (380vh scroll height).

**Lazy-loaded components** (performance optimization):
- `ApiReference`, `ChangelogTicker`, `Community`, `KnownLimitations`, `Roadmap`, `SystemRequirements`

### Hero Animation (`hero.tsx`)
- Scroll-driven animation: `h-[380vh]` container
- Phases: title shrinks from oversized → compact, services transition from constellation network → grid layout
- Uses CSS custom properties updated via `requestAnimationFrame` on scroll
- `prefers-reduced-motion` respected
- Service nodes show maturity badges (all currently "beta")

### Slammer Dashboard (`slammer-preview.tsx`)
- Client component with real-time simulated data
- Updates every 2 seconds (mission progress, logs, worker status)
- Tabs: Missions, Agents, Approvals
- Features: approve/deny, new mission, pause/resume
- **Data is simulated** — to connect to real backend, replace `useEffect` interval with API/WebSocket calls

### Mission Console (`mission-console.tsx`)
- Simulated mission replay (illustrative demo)
- Uses real service names and API endpoints
- Labeled as "Simulated replay" and "Illustrative replay"

### Header (`header.tsx`)
- Transparent at top, gains `bg-background/85 backdrop-blur-md` on scroll (>10px)
- Context-aware nav: shows section links on homepage, section titles on doc subpages
- Hamburger menu contains: Home, subpages (Install, Configuration, etc.), GitHub link
- Dark mode toggle and GitHub button always visible in top bar

---

## API Routes

| Route | Purpose | Cache |
|---|---|---|
| `GET /api/dashboard` | Mock dashboard data (JSON) | No cache |
| `GET /api/github-stats` | Live GitHub repo stats (stars, forks, contributors, size) | 1h ISR |
| `GET /api/releases-json` | Live GitHub releases (up to 10) | 1h ISR |
| `GET /api/releases` | Redirects to `/api/releases-json` | — |

GitHub API uses the public API (no auth required, rate-limited to 60 req/hour per IP).

---

## Data Sources

- **Services & versions:** `lib/evershade.ts` — manually maintained, verified against `version-manifest.json` in the real repo
- **Version:** `1.14.0` (matches real manifest)
- **GitHub stats:** Fetched live via API route
- **Releases:** Fetched live via API route
- **Mission replay script:** `lib/mission-script.ts` — uses real repo `LukaG712/Evershade`, branch `master`

---

## Deployment

### Netlify
- **URL:** https://evrshade.netlify.app
- **Build command:** `pnpm build`
- **Publish directory:** `.next`
- **Functions:** `netlify/functions` (for API routes)
- **Cache:** `.next/cache`, `node_modules/.cache`

### next.config.mjs
- `compress: true` — response compression
- `images.unoptimized: true` — no image optimization (Netlify doesn't support Next.js image optimization)
- `typescript.ignoreBuildErrors: true` — allows build to proceed despite TS errors
- Security headers: HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- Cache-Control: pages `must-revalidate`, static assets `max-age=31536000, immutable`

---

## TODO(luka) Markers

These are in the code, not rendered in the UI:

1. **`lib/evershade.ts:10`** — Confirm which services are stable vs beta
2. **`components/site/security.tsx:78`** — Add links to SECURITY.md, prompt-injection test suite, release signing verification
3. **`components/site/knowledge-graph.tsx:37`** — How is memory poisoning from untrusted scraped content prevented?

---

## Known Quirks

- **Hero scroll animation** uses `h-[380vh]` — very tall scroll container. Don't reduce this without adjusting the animation math.
- **Slammer dashboard** logs container uses `overflow-hidden` to prevent scroll-blocking. Logs update but don't auto-scroll.
- **Mission Console** log container also uses `overflow-hidden` for the same reason.
- **`comparison.tsx`** exists as dead code. The file was deleted from the homepage but may still exist in the repo.
- **`/subpage/compare`** route exists but only shows the migration guide. Metadata is stale.
- **`/api/github-stats`** route exists but is no longer used by the homepage (stats section was removed).
- **`/api/dashboard`** route exists but is only used by the mock dashboard simulation.

---

## Git & Committing

- Default branch: `master`
- When committing via Junie, it auto-adds `Co-authored-by: Junie <junie@jetbrains.com>`
- Remote: `origin`

---

## Notes

- This site is **not** the Evershade application itself — it's a marketing/documentation site.
- Real Evershade repo: https://github.com/LukaG712/Evershade
- Site repo is private.
- All service names, versions, and API endpoints should match the real Evershade codebase.
- No fabricated testimonials or fake data — everything is either real or clearly labeled as demo/simulation.
