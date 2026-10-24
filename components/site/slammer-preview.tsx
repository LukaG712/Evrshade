'use client'

import { Activity, CheckCircle, Clock, AlertTriangle, Terminal, BarChart3, Shield, Play, Pause, Plus, X, Search, ChevronDown, ChevronUp } from 'lucide-react'
import { useState, useEffect, useCallback, useRef } from 'react'
import { SectionHeading } from './section-heading'

type MissionStatus = 'running' | 'queued' | 'completed' | 'failed'
type ApprovalStatus = 'pending' | 'approved' | 'denied'

interface Mission {
  id: string
  name: string
  status: MissionStatus
  progress: number
  milestones: number
  currentMilestone: number
  startedAt: string
}

interface Agent {
  id: string
  name: string
  mission: string | null
  status: MissionStatus
}

interface Approval {
  id: string
  action: string
  status: ApprovalStatus
  reason: string
}

interface LogEntry {
  time: string
  service: string
  message: string
}

const INITIAL_MISSIONS: Mission[] = [
  { id: 'm_7f3a', name: 'Add rate limiting', status: 'running', progress: 67, milestones: 3, currentMilestone: 2, startedAt: '14:07' },
  { id: 'm_2e91', name: 'Update dependencies', status: 'queued', progress: 0, milestones: 2, currentMilestone: 0, startedAt: '—' },
  { id: 'm_4b1c', name: 'Refactor auth module', status: 'completed', progress: 100, milestones: 4, currentMilestone: 4, startedAt: '13:42' },
  { id: 'm_8d5f', name: 'Fix login timeout', status: 'failed', progress: 42, milestones: 2, currentMilestone: 1, startedAt: '13:55' },
]

const INITIAL_AGENTS: Agent[] = [
  { id: 'worker-1', name: 'worker-1', mission: 'm_7f3a', status: 'running' },
  { id: 'worker-2', name: 'worker-2', mission: null, status: 'queued' },
  { id: 'worker-3', name: 'worker-3', mission: null, status: 'queued' },
]

const INITIAL_APPROVALS: Approval[] = [
  { id: 'a_1', action: 'Install express@5.0', status: 'pending', reason: 'npm install express@5.0' },
  { id: 'a_2', action: 'Push to main branch', status: 'pending', reason: 'git push origin main' },
]

const LOG_MESSAGES: LogEntry[] = [
  { time: '14:07:23', service: 'greenie', message: 'mission m_7f3a · milestone 2/3 · feature "add middleware" started' },
  { time: '14:07:24', service: 'slinker', message: 'worker-1 · container created · alpine:3.20' },
  { time: '14:07:25', service: 'shrewd', message: 'route → planner model · cost $0.0012' },
  { time: '14:07:28', service: 'slinker', message: 'worker-1 · pytest -q · 12 passed in 2.4s' },
  { time: '14:07:30', service: 'hider', message: 'lease GITHUB_TOKEN · aes-256-gcm · ok' },
  { time: '14:07:32', service: 'greenie', message: 'mission m_7f3a · feature "add middleware" completed' },
  { time: '14:07:33', service: 'poltergeist', message: 'notification sent · slack · #devops' },
  { time: '14:07:35', service: 'gobber', message: 'embed batch · 8 chunks · 768 dims' },
  { time: '14:07:38', service: 'sneaker', message: 'metric: mission.duration · 14.2s' },
  { time: '14:07:40', service: 'greenie', message: 'mission m_7f3a · milestone 3/3 starting' },
  { time: '14:07:42', service: 'trapper', message: 'crawl docs · 3 pages · 1.2s' },
  { time: '14:07:45', service: 'slinker', message: 'worker-1 · eslint · 0 errors' },
]

function statusColor(status: string) {
  switch (status) {
    case 'running':
      return 'text-signal'
    case 'completed':
      return 'text-muted-foreground'
    case 'failed':
      return 'text-destructive'
    case 'pending':
      return 'text-muted-foreground/60'
    case 'approved':
      return 'text-signal'
    case 'denied':
      return 'text-destructive'
    default:
      return 'text-muted-foreground/60'
  }
}

function statusIcon(status: string) {
  switch (status) {
    case 'running':
      return <Play className="size-3" aria-hidden="true" />
    case 'completed':
      return <CheckCircle className="size-3" aria-hidden="true" />
    case 'failed':
      return <AlertTriangle className="size-3" aria-hidden="true" />
    case 'pending':
      return <Clock className="size-3" aria-hidden="true" />
    case 'approved':
      return <CheckCircle className="size-3" aria-hidden="true" />
    case 'denied':
      return <X className="size-3" aria-hidden="true" />
    default:
      return <Clock className="size-3" aria-hidden="true" />
  }
}

export function SlammerPreview() {
  const [missions, setMissions] = useState<Mission[]>(INITIAL_MISSIONS)
  const [agents] = useState<Agent[]>(INITIAL_AGENTS)
  const [approvals, setApprovals] = useState<Approval[]>(INITIAL_APPROVALS)
  const [logs, setLogs] = useState<LogEntry[]>(LOG_MESSAGES.slice(0, 5))
  const [expandedMission, setExpandedMission] = useState<string | null>(null)
  const [showNewMission, setShowNewMission] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [newMissionName, setNewMissionName] = useState('')
  const logIndexRef = useRef(5)
  const logContainerRef = useRef<HTMLDivElement>(null)

  // Simulate real-time log streaming
  useEffect(() => {
    const interval = setInterval(() => {
      setLogs(prev => {
        const nextIndex = logIndexRef.current % LOG_MESSAGES.length
        const newLog = LOG_MESSAGES[nextIndex]
        logIndexRef.current = nextIndex + 1
        const updated = [...prev, newLog]
        if (updated.length > 8) updated.shift()
        return updated
      })
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  // Auto-scroll logs
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs])

  // Simulate progress animation for running missions
  useEffect(() => {
    const interval = setInterval(() => {
      setMissions(prev =>
        prev.map(m => {
          if (m.status === 'running' && m.progress < 100) {
            const newProgress = Math.min(100, m.progress + Math.floor(Math.random() * 3) + 1)
            return { ...m, progress: newProgress }
          }
          if (m.status === 'running' && m.progress >= 100) {
            return { ...m, status: 'completed' as MissionStatus, progress: 100 }
          }
          return m
        })
      )
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleApprove = useCallback((id: string) => {
    setApprovals(prev =>
      prev.map(a => a.id === id ? { ...a, status: 'approved' as ApprovalStatus } : a)
    )
  }, [])

  const handleDeny = useCallback((id: string) => {
    setApprovals(prev =>
      prev.map(a => a.id === id ? { ...a, status: 'denied' as ApprovalStatus } : a)
    )
  }, [])

  const handleNewMission = useCallback(() => {
    if (!newMissionName.trim()) return
    const id = `m_${Math.random().toString(36).slice(2, 6)}`
    const newMission: Mission = {
      id,
      name: newMissionName.trim(),
      status: 'queued',
      progress: 0,
      milestones: 2,
      currentMilestone: 0,
      startedAt: '—',
    }
    setMissions(prev => [newMission, ...prev])
    setNewMissionName('')
    setShowNewMission(false)
  }, [newMissionName])

  const filteredMissions = missions.filter(m =>
    m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.id.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const activeMissions = missions.filter(m => m.status === 'running').length
  const activeWorkers = agents.filter(a => a.status === 'running').length
  const pendingApprovals = approvals.filter(a => a.status === 'pending').length

  return (
    <section id="slammer" aria-labelledby="slammer-title" className="px-4 pt-16 md:px-[max(24px,3vw)] md:pt-40">
      <SectionHeading
        id="slammer-title"
        label="Slammer"
        title={
          <>
            See everything.
            <br />
            <span className="text-muted-foreground">Control everything.</span>
          </>
        }
        lead="Slammer is the React web dashboard. Monitor missions, approve sensitive operations, watch agents work, and review logs - all from a single interface."
      />

      {/* Dashboard mockup */}
      <div className="mt-12 md:mt-24">
        <div className="overflow-hidden rounded-lg border border-border bg-background">
          {/* Title bar */}
          <div className="flex items-center gap-2 border-b border-border bg-foreground/[0.03] px-4 py-3">
            <div className="flex gap-1.5">
              <span className="size-2.5 rounded-full border border-foreground/30" />
              <span className="size-2.5 rounded-full border border-foreground/30" />
              <span className="size-2.5 rounded-full border border-foreground/30" />
            </div>
            <span className="ml-3 font-mono text-[11px] text-muted-foreground">Slammer - Evershade Dashboard</span>
          </div>

          {/* Top bar */}
          <div className="flex items-center justify-between border-b border-border px-3 py-2.5 sm:px-6 sm:py-3">
            <div className="flex items-center gap-2 sm:gap-4">
              <span className="flex items-center gap-1.5 font-mono text-[10px] sm:text-[11px] text-signal">
                <span className="size-1.5 animate-pulse rounded-full bg-signal sm:size-2" aria-hidden="true" />
                Live
              </span>
              <span className="font-mono text-[10px] sm:text-[11px] text-muted-foreground">{activeMissions} active</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowNewMission(true)}
                className="flex items-center gap-1 rounded border border-border px-2 py-1 sm:px-3 sm:py-1.5 font-mono text-[10px] uppercase tracking-wider hover:bg-foreground hover:text-background"
              >
                <Plus className="size-3" aria-hidden="true" />
                <span className="hidden sm:inline">New mission</span>
                <span className="sm:hidden">New</span>
              </button>
            </div>
          </div>

          {/* Stats bar */}
          <div className="grid grid-cols-2 gap-px border-b border-border bg-border sm:grid-cols-4">
            {[
              { label: 'Active missions', value: String(activeMissions), icon: Activity },
              { label: 'Workers', value: `${activeWorkers}/3`, icon: Terminal },
              { label: 'Pending approvals', value: String(pendingApprovals), icon: Shield },
              { label: 'Model cost today', value: '$0.04', icon: BarChart3 },
            ].map((stat) => {
              const Icon = stat.icon
              return (
                <div key={stat.label} className="flex items-center gap-2 bg-background px-3 py-3 sm:gap-3 sm:px-6 sm:py-4">
                  <Icon className="size-3.5 shrink-0 text-muted-foreground/60 sm:size-4" aria-hidden="true" />
                  <div className="min-w-0">
                    <p className="text-lg font-semibold tracking-tight sm:text-xl">{stat.value}</p>
                    <p className="truncate font-mono text-[10px] text-muted-foreground">{stat.label}</p>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Panels grid */}
          <div className="grid grid-cols-1 gap-px bg-border">
            {/* Missions panel */}
            <div className="bg-background">
              <div className="flex items-center justify-between border-b border-border px-3 py-2.5 sm:px-5 sm:py-3">
                <div className="flex items-center gap-2">
                  <Activity className="size-3.5 sm:size-4 text-muted-foreground/60" aria-hidden="true" />
                  <span className="font-mono text-[10px] sm:text-[11px] uppercase tracking-wider">Missions</span>
                </div>
                <span className="font-mono text-[10px] text-muted-foreground">{filteredMissions.length} items</span>
              </div>
              {/* Search */}
              <div className="border-b border-border px-3 py-2 sm:px-5">
                <div className="relative">
                  <Search className="absolute left-2 top-1/2 -translate-y-1/2 size-3 text-muted-foreground/40" aria-hidden="true" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search missions..."
                    className="w-full rounded border border-border bg-foreground/[0.03] pl-8 pr-3 py-1.5 font-mono text-[10px] placeholder:text-muted-foreground/40 focus:outline-none focus:ring-1 focus:ring-signal/50"
                  />
                </div>
              </div>
              <div className="divide-y divide-border">
                {filteredMissions.map((mission) => (
                  <div key={mission.id}>
                    <button
                      onClick={() => setExpandedMission(expandedMission === mission.id ? null : mission.id)}
                      className="w-full flex items-center justify-between px-3 py-2.5 sm:px-5 sm:py-3 hover:bg-foreground/[0.02] text-left"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <span className={`flex items-center gap-1.5 font-mono text-[11px] ${statusColor(mission.status)} shrink-0`}>
                          {statusIcon(mission.status)}
                        </span>
                        <span className="font-mono text-[11px] truncate">{mission.id}</span>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {mission.progress > 0 && mission.progress < 100 && (
                          <div className="hidden sm:flex items-center gap-2">
                            <div className="h-1.5 w-12 overflow-hidden rounded-full bg-border">
                              <div
                                className={`h-full rounded-full transition-all duration-1000 ${mission.status === 'failed' ? 'bg-destructive' : 'bg-signal'}`}
                                style={{ width: `${mission.progress}%` }}
                              />
                            </div>
                            <span className="font-mono text-[10px] text-muted-foreground">{mission.progress}%</span>
                          </div>
                        )}
                        {mission.progress > 0 && mission.progress < 100 && (
                          <span className="sm:hidden font-mono text-[10px] text-muted-foreground">{mission.progress}%</span>
                        )}
                        {mission.status === 'completed' && <span className="font-mono text-[10px] text-muted-foreground">Done</span>}
                        {mission.status === 'queued' && <span className="font-mono text-[10px] text-muted-foreground/60">Waiting</span>}
                        {mission.status === 'failed' && <span className="font-mono text-[10px] text-destructive">Failed</span>}
                        {expandedMission === mission.id ? (
                          <ChevronUp className="size-3 text-muted-foreground/40" aria-hidden="true" />
                        ) : (
                          <ChevronDown className="size-3 text-muted-foreground/40" aria-hidden="true" />
                        )}
                      </div>
                    </button>
                    {/* Expanded mission details */}
                    {expandedMission === mission.id && (
                      <div className="border-t border-border px-3 py-2.5 space-y-2 sm:px-5 sm:py-3">
                        <p className="font-mono text-[11px]">{mission.name}</p>
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <span className="font-mono text-[10px] text-muted-foreground">Milestones</span>
                            <p className="font-mono text-xs">{mission.currentMilestone}/{mission.milestones}</p>
                          </div>
                          <div>
                            <span className="font-mono text-[10px] text-muted-foreground">Started</span>
                            <p className="font-mono text-xs">{mission.startedAt}</p>
                          </div>
                        </div>
                        {mission.status === 'running' && (
                          <div className="pt-1">
                            <div className="h-1.5 w-full overflow-hidden rounded-full bg-border">
                              <div
                                className="h-full rounded-full bg-signal transition-all duration-1000"
                                style={{ width: `${mission.progress}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Agents panel */}
            <div className="bg-background">
              <div className="flex items-center justify-between border-b border-border px-3 py-2.5 sm:px-5 sm:py-3">
                <div className="flex items-center gap-2">
                  <Terminal className="size-3.5 sm:size-4 text-muted-foreground/60" aria-hidden="true" />
                  <span className="font-mono text-[10px] sm:text-[11px] uppercase tracking-wider">Agents</span>
                </div>
                <span className="font-mono text-[10px] text-muted-foreground">{agents.length} items</span>
              </div>
              <div className="divide-y divide-border">
                {agents.map((agent) => (
                  <div key={agent.id} className="flex items-center justify-between px-3 py-2.5 sm:px-5 sm:py-3">
                    <div className="flex items-center gap-2">
                      <span className={`flex items-center gap-1.5 font-mono text-[11px] ${statusColor(agent.status)}`}>
                        {statusIcon(agent.status)}
                        {agent.name}
                      </span>
                    </div>
                    <span className="font-mono text-[10px] text-muted-foreground">
                      {agent.mission ? `· ${agent.mission}` : '· idle'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Approvals panel */}
            <div className="bg-background">
              <div className="flex items-center justify-between border-b border-border px-3 py-2.5 sm:px-5 sm:py-3">
                <div className="flex items-center gap-2">
                  <Shield className="size-3.5 sm:size-4 text-muted-foreground/60" aria-hidden="true" />
                  <span className="font-mono text-[10px] sm:text-[11px] uppercase tracking-wider">Approvals</span>
                </div>
                <span className="font-mono text-[10px] text-muted-foreground">{approvals.length} items</span>
              </div>
              <div className="divide-y divide-border">
                {approvals.map((approval) => (
                  <div key={approval.id} className="px-3 py-2.5 sm:px-5 sm:py-3">
                    <div className="flex items-center justify-between">
                      <span className={`flex items-center gap-1.5 font-mono text-[11px] ${statusColor(approval.status)}`}>
                        {statusIcon(approval.status)}
                        {approval.action}
                      </span>
                    </div>
                    {approval.status === 'pending' ? (
                      <div className="mt-2 space-y-1">
                        <code className="block rounded bg-foreground/[0.05] px-2 py-1 font-mono text-[10px] text-muted-foreground">
                          {approval.reason}
                        </code>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleApprove(approval.id)}
                            className="flex-1 rounded border border-signal/30 bg-signal/5 px-2 py-1 font-mono text-[10px] text-signal-ink hover:bg-signal/10"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleDeny(approval.id)}
                            className="flex-1 rounded border border-destructive/30 bg-destructive/5 px-2 py-1 font-mono text-[10px] text-destructive hover:bg-destructive/10"
                          >
                            Deny
                          </button>
                        </div>
                      </div>
                    ) : (
                      <span className="font-mono text-[10px] text-muted-foreground capitalize">{approval.status}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom log area */}
          <div className="border-t border-border">
            <div className="flex items-center justify-between border-b border-border px-3 py-2 sm:px-5 sm:py-2">
              <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Live logs</span>
              <span className="flex items-center gap-1.5 font-mono text-[10px] text-muted-foreground/60">
                <span className="size-1.5 animate-pulse rounded-full bg-signal" aria-hidden="true" />
                SSE stream
              </span>
            </div>
            <div
              ref={logContainerRef}
              className="max-h-24 overflow-y-auto bg-foreground/[0.02] p-3 font-mono text-[9px] leading-relaxed text-muted-foreground sm:max-h-32 sm:p-4 sm:text-[10px]"
            >
              {logs.map((log, i) => (
                <p key={i} className={i === logs.length - 1 ? 'text-foreground' : ''}>
                  <span className="text-muted-foreground/40">{log.time}</span>{' '}
                  <span className="text-signal">{log.service}</span>{' '}
                  {log.message}
                </p>
              ))}
            </div>
          </div>
        </div>

        {/* New mission modal */}
        {showNewMission && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
            <div className="w-full max-w-md rounded-lg border border-border bg-background p-6 shadow-lg">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold tracking-tight">New mission</h3>
                <button
                  onClick={() => setShowNewMission(false)}
                  className="rounded p-1 hover:bg-foreground/[0.05]"
                >
                  <X className="size-4" aria-hidden="true" />
                </button>
              </div>
              <div className="mt-4 space-y-3">
                <div>
                  <label className="block font-mono text-[10px] text-muted-foreground mb-1">Mission name</label>
                  <input
                    type="text"
                    value={newMissionName}
                    onChange={(e) => setNewMissionName(e.target.value)}
                    placeholder="e.g. Add caching layer"
                    className="w-full rounded border border-border bg-foreground/[0.03] px-3 py-2 font-mono text-sm placeholder:text-muted-foreground/40 focus:outline-none focus:ring-1 focus:ring-signal/50"
                    onKeyDown={(e) => e.key === 'Enter' && handleNewMission()}
                    autoFocus
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleNewMission}
                    disabled={!newMissionName.trim()}
                    className="flex-1 rounded bg-signal/10 border border-signal/30 px-4 py-2 font-mono text-sm text-signal-ink hover:bg-signal/20 disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    Create mission
                  </button>
                  <button
                    onClick={() => setShowNewMission(false)}
                    className="rounded border border-border px-4 py-2 font-mono text-sm hover:bg-foreground/[0.05]"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <p className="mt-4 font-mono text-[10px] text-muted-foreground">{'Slammer runs on port 5173. Accessible via browser or reverse proxy. SSE streaming for real-time updates.'}</p>
      </div>

      {/* Features list */}
      <div className="mt-12 grid gap-4 md:mt-16 md:grid-cols-3">
        {[
          {
            title: 'Mission overview',
            body: 'See every mission\'s status, progress, and timeline at a glance. Filter by status, search by name, and drill into details.',
          },
          {
            title: 'Approval queue',
            body: 'Sensitive operations wait here. Review the concrete action - not model-written justification - and approve or deny with one click.',
          },
          {
            title: 'Live logs',
            body: 'Server-Sent Events stream logs from all services in real time. Secret redaction is applied automatically.',
          },
        ].map((feature) => (
          <div key={feature.title} className="border-t border-foreground pt-6">
            <h3 className="text-lg font-semibold tracking-tight">{feature.title}</h3>
            <p className="mt-2 text-sm leading-snug text-muted-foreground">{feature.body}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
