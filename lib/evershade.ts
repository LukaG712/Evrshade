export const VERSION = '1.14.0'
export const REPO_URL = 'https://github.com/LukaG712/Evershade'
export const SITE_URL = 'https://evrshade.netlify.app'

/** Last verified date for comparison tables and documentation claims. */
export const LAST_VERIFIED = 'October 2025'

export type ServiceMaturity = 'stable' | 'beta' | 'experimental'

/** Per-service maturity. TODO(luka): Confirm which services are stable vs beta. */
export const SERVICE_MATURITY: Record<string, ServiceMaturity> = {
  greenie: 'beta',
  slinker: 'beta',
  trapper: 'beta',
  gobber: 'beta',
  shrewd: 'beta',
  sneaker: 'beta',
  hider: 'beta',
  poltergeist: 'beta',
  slammer: 'beta',
  speedy: 'beta',
}

export type ServiceTier = 'orchestrator' | 'core' | 'optional' | 'client'

export type Service = {
  id: string
  name: string
  port: string
  role: string
  stack: string
  tier: ServiceTier
}

export const SERVICES: Service[] = [
  { id: 'greenie', name: 'Greenie', port: '8080', role: 'Central orchestrator & API backend', stack: 'Python / FastAPI', tier: 'orchestrator' },
  { id: 'slinker', name: 'Slinker', port: '8000', role: 'Code execution engine', stack: 'Python / FastAPI', tier: 'core' },
  { id: 'trapper', name: 'Trapper', port: '3000', role: 'Web scraping & crawling (optional Redis for caching)', stack: 'TypeScript / Fastify', tier: 'core' },
  { id: 'gobber', name: 'Gobber', port: '8085', role: 'Persistent storage & knowledge graph', stack: 'Python / FastAPI', tier: 'core' },
  { id: 'shrewd', name: 'Shrewd', port: '8089', role: 'LLM provider abstraction', stack: 'Python / FastAPI', tier: 'optional' },
  { id: 'sneaker', name: 'Sneaker', port: '8086', role: 'Metrics, traces, logs', stack: 'Python / FastAPI', tier: 'optional' },
  { id: 'hider', name: 'Hider', port: '8087', role: 'Encrypted secrets management', stack: 'Python / FastAPI', tier: 'optional' },
  { id: 'poltergeist', name: 'Poltergeist', port: '8088', role: 'Notifications & async delivery', stack: 'Python / FastAPI', tier: 'optional' },
  { id: 'slammer', name: 'Slammer', port: '5173', role: 'React web dashboard', stack: 'React / TypeScript', tier: 'client' },
  { id: 'speedy', name: 'Speedy', port: 'CLI', role: 'The evershade command', stack: 'Python / Click / Rich', tier: 'client' },
]

/** Dependency edges taken from version-manifest.json. [from, to] by index into SERVICES. */
export const EDGES: [number, number][] = [
  [0, 1],
  [0, 2],
  [0, 3],
  [0, 4],
  [0, 5],
  [0, 6],
  [0, 7],
  [3, 4],
  [8, 0],
  [9, 0],
]

export const TIER_LABEL: Record<ServiceTier, string> = {
  orchestrator: 'Orchestrator',
  core: 'Core',
  optional: 'Optional',
  client: 'Interface',
}

export const MISSION_STAGES = [
  {
    name: 'Create',
    endpoint: 'POST /api/missions',
    body: 'Define a mission. Large tasks are broken down into milestones and features.',
  },
  {
    name: 'Plan',
    endpoint: 'POST /api/missions/{id}/plan',
    body: 'LLM-based planning via Shrewd, with repository intelligence and a heuristic fallback.',
  },
  {
    name: 'Execute',
    endpoint: 'POST /api/missions/{id}/execute',
    body: 'Milestones run their features with parallel workers. Logs stream live over SSE.',
  },
  {
    name: 'Validate',
    endpoint: 'POST /api/missions/{id}/validate',
    body: 'Deterministic checks (test, lint, type) plus a diff-based security review.',
  },
  {
    name: 'Fix-Revalidate',
    endpoint: 'POST /api/missions/{id}/fix-revalidate',
    body: 'Failures become fix features automatically, then re-run, with configurable retries.',
  },
  {
    name: 'Complete',
    endpoint: 'GET /api/missions/analytics',
    body: 'When every check passes, the mission completes. Duration, model usage and outcomes are recorded.',
  },
] as const

export const MISSION_CAPABILITIES = [
  ['Mission lifecycle', 'Create, plan, execute, validate, complete, cancel, pause and resume.'],
  ['Approval gates', 'Human-in-the-loop approval for sensitive operations, with three autonomy levels.'],
  ['Code review', 'Automated test, lint and type checks and a diff-based security review.'],
  ['Checkpoint recovery', 'Mission state is persisted so a mission can recover from failures.'],
  ['SSE streaming', 'Real-time mission execution logs via Server-Sent Events.'],
  ['Secret redaction', 'Pattern-based redaction of API keys, tokens and passwords in logs.'],
] as const

export const PRINCIPLES = [
  ['Modular services', 'Each service has a clear boundary and public interface.'],
  ['SQLite-first', 'SQLite where it satisfies requirements. Other databases only when necessary.'],
  ['No heavy infrastructure', 'No Kubernetes, Kafka, Elasticsearch or distributed databases without a concrete need.'],
  ['Self-hosted practical', 'Runs on ordinary developer hardware without excessive resource consumption.'],
  ['Security by default', 'Least privilege, network isolation and container hardening as the default.'],
] as const

export const PROFILES = [
  { name: 'Minimal', detail: 'Core only: Greenie, Slinker, Trapper, Gobber', flag: '--profile minimal' },
  { name: 'Standard', detail: 'Core + optional services (no dashboard)', flag: '--profile standard' },
  { name: 'Full', detail: 'All services including Slammer dashboard', flag: '--profile full' },
  { name: 'Custom', detail: 'Pick individual services', flag: '--profile custom' },
  { name: '+ Ollama', detail: 'Local LLM support', flag: '--profile ollama' },
  { name: '+ Proxy', detail: 'Caddy reverse proxy with TLS', flag: '--profile proxy' },
] as const

/** Live activity shown on each service cell at the end of the hero. Illustrative, mirrors real endpoints. */
export const LIVE_ACTIVITY: Record<string, string[]> = {
  greenie: ['mission m_7f3a · executing', 'milestone 2/3 · 3 workers', 'validate → fix-revalidate'],
  slinker: ['worker-1 · pytest -q', 'worker-2 · ruff check .', 'worker-3 · mypy src/'],
  trapper: ['crawl docs · 14 pages', 'ssrf guard · 1 blocked', 'extract · markdown'],
  gobber: ['hybrid search · 0.21s', 'embed batch · 64 chunks', 'graph link · resolved'],
  shrewd: ['route → planner model', 'cost · $0.0041', 'privacy · local-only'],
  sneaker: ['trace 9f2c · 48 spans', 'otlp · redacted', 'alert rules · 0 firing'],
  hider: ['lease GITHUB_TOKEN', 'aes-256-gcm · ok', 'redact · 2 matches'],
  poltergeist: ['slack · milestone done', 'telegram · queued', 'email · delivered'],
  slammer: ['sse · /logs/stream', 'missions · 1 active', 'approvals · 1 pending'],
  speedy: ['$ evershade status', '$ evershade doctor', '$ evershade logs greenie'],
}

export const AUTONOMY = [
  {
    id: 'supervised',
    name: 'Supervised',
    rule: 'Every operation requires approval.',
  },
  {
    id: 'restricted',
    name: 'Restricted',
    rule: 'Only sensitive operations require approval.',
  },
  {
    id: 'full',
    name: 'Full',
    rule: 'No approval gates.',
  },
] as const

export type AutonomyId = (typeof AUTONOMY)[number]['id']

/** Example operations. Which ones count as "sensitive" is illustrative. */
export const OPERATIONS: { op: string; sensitive: boolean }[] = [
  { op: 'Read repository files', sensitive: false },
  { op: 'Run tests, lint and type checks', sensitive: false },
  { op: 'Write files inside the task workspace', sensitive: false },
  { op: 'Install a new dependency', sensitive: true },
  { op: 'Use a secret from Hider', sensitive: true },
  { op: 'Push a branch or open a pull request', sensitive: true },
]

export const ISOLATION = [
  { level: 'worktree', boundary: 'None. Shares the host filesystem', use: 'Trusted development only', strength: 0 },
  { level: 'container', boundary: 'Isolated container', use: 'Default for untrusted code', strength: 1 },
  { level: 'workstation', boundary: 'Full VM isolation', use: 'Maximum isolation', strength: 2 },
] as const

export const INJECTION_RULES = [
  'Untrusted content cannot trigger tool calls',
  'Untrusted content cannot grant or bypass approvals',
  'Untrusted content cannot change permissions or request secrets',
  'Approval prompts show the concrete action, not model-written justification',
  'Planning (reading untrusted content) is separated from execution (side effects)',
] as const

export const PANIC_STEPS = [
  'Pause all workflow execution and triggers',
  'Cancel running Slinker jobs and clean up sandboxes',
  'Optionally revoke active sessions and tokens',
  'Record an audit event',
  'Notify via Poltergeist, if available',
] as const

export const HARDENING = [
  'Read-only root filesystem',
  'Dropped Linux capabilities',
  'tmpfs scratch space',
  'Default-deny workstation network',
  'SSRF + metadata endpoint blocking',
  'CSRF protection',
  'Auth rate limiting',
  'Idempotency keys',
  'Secret redaction in logs + model context',
  'Credential rotation',
  'Release signing + provenance',
  'Prompt-injection test suite',
] as const

export type Integration = { name: string; note?: string; status: 'shipped' | 'extensible' }

export const INTEGRATIONS: { group: string; via: string; detail: string; items: Integration[] }[] = [
  {
    group: 'Models',
    via: 'Shrewd',
    detail: 'Model routing with cost tracking and privacy classification. OpenAI-compatible /v1/chat/completions.',
    items: [
      { name: 'OpenAI', status: 'shipped' },
      { name: 'Anthropic', status: 'shipped' },
      { name: 'Google', status: 'shipped' },
      { name: 'Ollama', note: 'local', status: 'shipped' },
    ],
  },
  {
    group: 'Delivery',
    via: 'Poltergeist',
    detail: 'Async notifications with SQLite persistence. Also receives alerts from Sneaker.',
    items: [
      { name: 'Slack', status: 'shipped' },
      { name: 'Discord', status: 'shipped' },
      { name: 'Email / SMTP', status: 'shipped' },
      { name: 'Telegram', status: 'shipped' },
    ],
  },
  {
    group: 'Triggers',
    via: 'Greenie',
    detail: 'Automation engine with idempotency and rate limiting. Starts workflows and missions.',
    items: [
      { name: 'GitHub webhooks', status: 'shipped' },
      { name: 'Schedules', status: 'shipped' },
      { name: 'File changes', status: 'shipped' },
      { name: 'Webhooks', status: 'shipped' },
    ],
  },
  {
    group: 'Tools',
    via: 'Greenie',
    detail: 'Agents invoke tools exposed by MCP servers. Plugins register through the plugin registry.',
    items: [
      { name: 'MCP', note: 'stdio', status: 'shipped' },
      { name: 'MCP', note: 'sse', status: 'shipped' },
      { name: 'Plugin registry', status: 'shipped' },
    ],
  },
  {
    group: 'Runners',
    via: 'Slinker',
    detail: 'Pluggable runner interface. Junie is the default; the abstraction is built for more.',
    items: [
      { name: 'Junie', note: 'default', status: 'shipped' },
      { name: 'Ollama', status: 'extensible' },
      { name: 'Custom runners', status: 'extensible' },
    ],
  },
  {
    group: 'Observability',
    via: 'Sneaker',
    detail: 'Metrics, traces and logs with secret redaction. Alert rules with deduplication and cooldown.',
    items: [
      { name: 'OTLP', status: 'shipped' },
      { name: 'Alert rules', status: 'shipped' },
    ],
  },
]

export const ROADMAP = [
  { phase: 1, name: 'Foundations', items: ['Architecture docs', 'Version manifest', 'Compose profiles + hardening'] },
  { phase: 2, name: 'Security & persistence', items: ['AES-256-GCM secrets', 'Bearer auth everywhere', 'SSRF protection'] },
  { phase: 3, name: 'Real implementation', items: ['LLM providers', 'Notification delivery', 'Full CLI'] },
  { phase: 4, name: 'Workflow engine', items: ['Triggers', 'Visual builder', 'Approval gates'] },
  { phase: 5, name: 'Agent workstations', items: ['Container driver', 'Default-deny network', 'Live terminal + desktop'] },
  { phase: 6, name: 'Quality & release', items: ['Security tests', 'Agent eval suite', 'Release signing'] },
  { phase: 7, name: 'UI & extensibility', items: ['Single dashboard', 'MCP + plugins', 'Ops dashboards'] },
  { phase: 8, name: 'Hardening', items: ['Emergency stop', 'Activity timeline', 'Credential rotation'] },
  { phase: 9, name: 'Mission lifecycle', items: ['Fix-revalidate', 'SSE streaming'] },
] as const

export const OPEN_ITEMS = ['Sneaker: SQLite persistence for metrics, traces and logs'] as const
