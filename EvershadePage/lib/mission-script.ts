export type FeatureStatus = 'hidden' | 'queued' | 'running' | 'done' | 'failed' | 'blocked'
export type CheckStatus = 'idle' | 'running' | 'pass' | 'fail'
export type CheckId = 'tests' | 'lint' | 'types' | 'security'
export type LogLevel = 'info' | 'ok' | 'warn' | 'err'

export type MissionEvent =
  | { d: number; type: 'log'; svc: string; text: string; level?: LogLevel }
  | { d: number; type: 'feature'; id: string; status: FeatureStatus; worker?: number }
  | { d: number; type: 'check'; id: CheckId; status: CheckStatus }
  | { d: number; type: 'phase'; phase: string }
  | { d: number; type: 'gate' }

export type Feature = { id: string; title: string; initial: FeatureStatus }

export const MISSION = {
  id: 'm_7f3a',
  title: 'Add rate limiting to the public API',
  repo: 'acme/api',
  branch: 'feat/rate-limit',
}

export const MILESTONES: { id: string; title: string; features: Feature[] }[] = [
  {
    id: 'M1',
    title: 'Research & plan',
    features: [
      { id: 'F1.1', title: 'Analyze repository', initial: 'queued' },
      { id: 'F1.2', title: 'Draft spec + validation contract', initial: 'queued' },
    ],
  },
  {
    id: 'M2',
    title: 'Implement',
    features: [
      { id: 'F2.1', title: 'Token-bucket middleware', initial: 'queued' },
      { id: 'F2.2', title: 'SQLite counter store', initial: 'queued' },
      { id: 'F2.3', title: 'Configuration + docs', initial: 'queued' },
      { id: 'F2.4', title: 'Fix: window reset off-by-one', initial: 'hidden' },
    ],
  },
  {
    id: 'M3',
    title: 'Validate & ship',
    features: [
      { id: 'F3.1', title: 'Run validation contract', initial: 'queued' },
      { id: 'F3.2', title: 'Push branch + open pull request', initial: 'queued' },
    ],
  },
]

export const CHECKS: { id: CheckId; label: string; cmd: string }[] = [
  { id: 'tests', label: 'Tests', cmd: 'pytest -q' },
  { id: 'lint', label: 'Lint', cmd: 'ruff check .' },
  { id: 'types', label: 'Types', cmd: 'mypy src/' },
  { id: 'security', label: 'Security review', cmd: 'diff-based' },
]

export const GATE = {
  actor: 'Slinker · worker 1',
  action: `git push origin ${MISSION.branch} && open pull request`,
  reason: 'Push to remote is a sensitive operation under Restricted autonomous.',
}

const log = (d: number, svc: string, text: string, level: LogLevel = 'info'): MissionEvent => ({
  d,
  type: 'log',
  svc,
  text,
  level,
})
const feat = (d: number, id: string, status: FeatureStatus, worker?: number): MissionEvent => ({
  d,
  type: 'feature',
  id,
  status,
  worker,
})
const check = (d: number, id: CheckId, status: CheckStatus): MissionEvent => ({ d, type: 'check', id, status })
const phase = (d: number, p: string): MissionEvent => ({ d, type: 'phase', phase: p })

export const SCRIPT: MissionEvent[] = [
  phase(200, 'Planning'),
  log(300, 'greenie', `POST /api/missions → 201 ${MISSION.id}`),
  log(500, 'greenie', 'autonomy=restricted · max_retries=2 · workers=3'),
  feat(400, 'F1.1', 'running', 1),
  log(600, 'gobber', 'hybrid search "rate limit middleware" · 12 hits · 0.21s'),
  log(700, 'slinker', 'repo intel · fastapi · 142 files · pytest detected'),
  feat(500, 'F1.1', 'done'),
  feat(200, 'F1.2', 'running', 1),
  log(600, 'shrewd', 'route planner → anthropic · privacy=internal · $0.0041'),
  log(800, 'greenie', 'plan ready · 3 milestones · 7 features · contract: test lint type security', 'ok'),
  feat(400, 'F1.2', 'done'),
  phase(300, 'Executing'),
  feat(200, 'F2.1', 'running', 1),
  feat(150, 'F2.2', 'running', 2),
  feat(150, 'F2.3', 'running', 3),
  log(500, 'slinker', 'w1 · container · edit src/api/middleware/ratelimit.py'),
  log(500, 'slinker', 'w2 · container · edit src/store/counters.py'),
  log(600, 'trapper', 'fetch starlette middleware docs · ssrf guard ok'),
  log(500, 'hider', 'lease DATABASE_URL → w2 · value [REDACTED]'),
  log(600, 'slinker', 'w3 · edit docs/CONFIGURATION.md (+24)'),
  feat(500, 'F2.3', 'done'),
  log(500, 'slinker', 'w2 · migration 0007_rate_counters.sql'),
  feat(500, 'F2.2', 'done'),
  log(500, 'slinker', 'w1 · wire middleware into app factory'),
  feat(600, 'F2.1', 'done'),
  phase(300, 'Validating'),
  feat(200, 'F3.1', 'running', 1),
  check(200, 'tests', 'running'),
  check(100, 'lint', 'running'),
  check(100, 'types', 'running'),
  check(100, 'security', 'running'),
  log(700, 'slinker', 'ruff check . · 0 issues'),
  check(100, 'lint', 'pass'),
  log(600, 'slinker', 'mypy src/ · success: no issues in 61 files'),
  check(100, 'types', 'pass'),
  log(800, 'slinker', 'pytest -q · 1 failed, 47 passed · test_window_reset', 'err'),
  check(100, 'tests', 'fail'),
  feat(100, 'F3.1', 'failed'),
  log(600, 'greenie', 'diff review · no secrets · no new egress', 'ok'),
  check(100, 'security', 'pass'),
  phase(500, 'Fix-revalidate'),
  log(300, 'greenie', 'validation failed → fix feature F2.4 · retry 1/2', 'warn'),
  feat(300, 'F2.4', 'running', 2),
  log(700, 'slinker', 'w2 · bucket refilled one tick early in window reset'),
  log(700, 'slinker', 'w2 · patch src/api/middleware/ratelimit.py (+3 −1)'),
  feat(500, 'F2.4', 'done'),
  phase(300, 'Validating'),
  feat(100, 'F3.1', 'running', 1),
  check(100, 'tests', 'running'),
  log(900, 'slinker', 'pytest -q · 48 passed', 'ok'),
  check(100, 'tests', 'pass'),
  feat(200, 'F3.1', 'done'),
  log(400, 'sneaker', 'trace 9f2c · 48 spans exported · secrets redacted'),
  feat(400, 'F3.2', 'running', 1),
  phase(100, 'Awaiting approval'),
  { d: 400, type: 'gate' },
]

export const APPROVE_TAIL: MissionEvent[] = [
  phase(100, 'Executing'),
  log(200, 'greenie', 'approval granted · audit evt_31', 'ok'),
  log(800, 'slinker', `w1 · pushed ${MISSION.branch} · pull request #128 opened`),
  feat(400, 'F3.2', 'done'),
  log(500, 'poltergeist', `slack #eng · mission ${MISSION.id} complete`),
  log(300, 'greenie', 'mission complete · 7/7 features · 1 fix cycle', 'ok'),
  phase(100, 'Complete'),
]

export const REJECT_TAIL: MissionEvent[] = [
  log(200, 'greenie', 'approval rejected · audit evt_31', 'warn'),
  feat(300, 'F3.2', 'blocked'),
  log(400, 'poltergeist', `slack #eng · ${MISSION.id} paused for review`),
  phase(100, 'Paused'),
]
