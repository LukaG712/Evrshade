'use client'

import { memo, useState, useEffect, useCallback } from 'react'
import { Activity, CheckCircle, Clock, AlertTriangle, Terminal, BarChart3, Shield, Play, Pause, ChevronDown, ChevronRight, X } from 'lucide-react'
import { SectionHeading } from './section-heading'
import { DashboardData, Mission, Agent, Approval, LogEntry, generateInitialData } from '@/lib/dashboard'

const StatItem = memo(({ label, value, icon: Icon }: { label: string; value: string; icon: typeof Activity }) => (
  <div className="flex items-center gap-3 bg-background px-6 py-4">
    <Icon className="size-4 text-muted-foreground/60" aria-hidden="true" />
    <div>
      <p className="text-xl font-semibold tracking-tight">{value}</p>
      <p className="font-mono text-[10px] text-muted-foreground">{label}</p>
    </div>
  </div>
))

function statusColor(status: string) {
  switch (status) {
    case 'running':
      return 'text-signal'
    case 'completed':
      return 'text-muted-foreground'
    case 'failed':
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
    default:
      return <Clock className="size-3" aria-hidden="true" />
  }
}

// Simulated log messages for real-time updates
const SIMULATED_LOGS = [
  { service: 'greenie', message: 'mission m_7f3a · milestone 3/3 · feature "deploy middleware" started' },
  { service: 'slinker', message: 'worker-1 · npm test · 24 passed in 3.1s' },
  { service: 'shrewd', message: 'route → code model · cost $0.0008' },
  { service: 'slinker', message: 'worker-1 · ruff check . · no issues' },
  { service: 'hider', message: 'redact · 0 matches in output' },
  { service: 'greenie', message: 'mission m_7f3a · milestone 3/3 · completed' },
  { service: 'slinker', message: 'worker-1 · idle · awaiting next task' },
  { service: 'sneaker', message: 'trace m_7f3a · 127 spans · duration 42s' },
  { service: 'gobber', message: 'embed batch · 128 chunks · 0.34s' },
  { service: 'poltergeist', message: 'slack · mission m_7f3a completed' },
  { service: 'greenie', message: 'mission m_2e91 · dequeued · starting execution' },
  { service: 'slinker', message: 'worker-2 · container created · alpine:3.20' },
  { service: 'shrewd', message: 'route → planner model · cost $0.0015' },
  { service: 'slinker', message: 'worker-2 · npm ci · 142 packages in 5.2s' },
  { service: 'hider', message: 'lease NPM_TOKEN · aes-256-gcm · ok' },
]

let logIndex = 0

const STATS_CONFIG = [
  { label: 'Active missions', icon: Activity },
  { label: 'Workers', icon: Terminal },
  { label: 'Pending approvals', icon: Shield },
  { label: 'Model cost today', icon: BarChart3 },
] as const

const TABS = ['missions', 'agents', 'approvals'] as const
const TAB_ICONS = { missions: Activity, agents: Terminal, approvals: Shield }

const FEATURES = [
  {
    title: 'Mission overview',
    body: "See every mission's status, progress, and timeline at a glance. Filter by status, search by name, and drill into details.",
  },
  {
    title: 'Approval queue',
    body: 'Sensitive operations wait here. Review the concrete action — not model-written justification — and approve or deny with one click.',
  },
  {
    title: 'Demo logs',
    body: 'Simulated Server-Sent Events stream showing what real-time logs look like. Secret redaction is applied automatically.',
  },
] as const

function getNextLog(): LogEntry {
  const log = SIMULATED_LOGS[logIndex % SIMULATED_LOGS.length]
  logIndex++
  const now = new Date()
  const timestamp = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
  return { timestamp, ...log }
}

export function SlammerPreview() {
  const [data, setData] = useState<DashboardData>(generateInitialData())
  const [expandedMission, setExpandedMission] = useState<string | null>(null)
  const [paused, setPaused] = useState(false)
  const [activeTab, setActiveTab] = useState<'missions' | 'agents' | 'approvals'>('missions')
  const [notification, setNotification] = useState<string | null>(null)

  // Simulate real-time updates
  useEffect(() => {
    if (paused) return

    const interval = setInterval(() => {
      setData((prev) => {
        const newLogs = [...prev.logs, getNextLog()].slice(-20)

        // Update mission progress
        const newMissions = prev.missions.map((m) => {
          if (m.status === 'running' && m.progress < 100) {
            const newProgress = Math.min(m.progress + Math.floor(Math.random() * 5) + 1, 100)
            return {
              ...m,
              progress: newProgress,
              status: newProgress >= 100 ? 'completed' : m.status,
              currentMilestone: newProgress >= 100 ? m.milestones : m.currentMilestone,
              modelCost: m.modelCost + Math.random() * 0.001,
            }
          }
          return m
        })

        // Move queued mission to running if a mission completed
        const hasCompleted = newMissions.some((m) => m.status === 'completed' && prev.missions.find((pm) => pm.id === m.id)?.status !== 'completed')
        const hasQueued = newMissions.some((m) => m.status === 'queued')

        if (hasCompleted && hasQueued) {
          newMissions.forEach((m, i) => {
            if (m.status === 'queued') {
              newMissions[i] = { ...m, status: 'running', startTime: new Date().toTimeString().slice(0, 8), workers: ['worker-2'] }
            }
          })
        }

        // Update agents
        const newAgents = prev.agents.map((a) => {
          const mission = newMissions.find((m) => m.status === 'running' && m.workers.includes(a.id))
          if (mission && a.status === 'idle') {
            return { ...a, status: 'running' as const, missionId: mission.id, tasksCompleted: a.tasksCompleted + 1 }
          }
          if (!mission && a.status === 'running' && a.missionId === mission?.id) {
            return { ...a, status: 'idle' as const, missionId: null }
          }
          return a
        })

        const workersBusy = newAgents.filter((a) => a.status === 'running').length

        return {
          ...prev,
          missions: newMissions,
          agents: newAgents,
          logs: newLogs,
          stats: {
            ...prev.stats,
            activeMissions: newMissions.filter((m) => m.status === 'running').length,
            workersBusy,
            workersTotal: newAgents.length,
            modelCostToday: prev.stats.modelCostToday + 0.0001,
          },
        }
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [paused])


  const handleApprove = useCallback((approvalId: string, action: string) => {
    setData((prev) => ({
      ...prev,
      approvals: prev.approvals.filter((a) => a.id !== approvalId),
      stats: {
        ...prev.stats,
        pendingApprovals: Math.max(0, prev.stats.pendingApprovals - 1),
      },
    }))
    setNotification(`Approved: ${action}`)
    setTimeout(() => setNotification(null), 3000)
  }, [])

  const handleDeny = useCallback((approvalId: string, action: string) => {
    setData((prev) => ({
      ...prev,
      approvals: prev.approvals.filter((a) => a.id !== approvalId),
      stats: {
        ...prev.stats,
        pendingApprovals: Math.max(0, prev.stats.pendingApprovals - 1),
      },
    }))
    setNotification(`Denied: ${action}`)
    setTimeout(() => setNotification(null), 3000)
  }, [])

  const handleNewMission = useCallback(() => {
    const id = `m_${Math.random().toString(36).slice(2, 6)}`
    setData((prev) => {
      const newMission: Mission = {
        id,
        name: 'New mission',
        status: 'queued',
        progress: 0,
        milestones: 2,
        currentMilestone: 0,
        workers: [],
        startTime: '-',
        modelCost: 0,
      }
      return {
        ...prev,
        missions: [...prev.missions, newMission],
      }
    })
    setNotification('New mission queued')
    setTimeout(() => setNotification(null), 3000)
  }, [])

  const handlePauseAll = useCallback(() => {
    setPaused((p) => !p)
    setNotification(paused ? 'Resumed all missions' : 'Paused all missions')
    setTimeout(() => setNotification(null), 3000)
  }, [paused])

  const toggleMission = useCallback((id: string) => {
    setExpandedMission((prev) => (prev === id ? null : id))
  }, [])

  const { missions, agents, approvals, logs, stats } = data

  return (
    <section id="slammer" aria-labelledby="slammer-title" className="px-4 pt-32 md:px-[max(24px,3vw)] md:pt-48">
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
        lead="Slammer is the React web dashboard. Monitor missions, approve sensitive operations, watch agents work, and review logs — all from a single interface."
      />

      {/* Dashboard */}
      <div className="mt-16 md:mt-24">
        <div className="overflow-hidden rounded-lg border border-border bg-background">
          {/* Title bar */}
          <div className="flex items-center gap-2 border-b border-border bg-foreground/[0.03] px-4 py-3">
            <div className="flex gap-1.5">
              <span className="size-2.5 rounded-full border border-foreground/30" />
              <span className="size-2.5 rounded-full border border-foreground/30" />
              <span className="size-2.5 rounded-full border border-foreground/30" />
            </div>
            <span className="ml-3 font-mono text-[11px] text-muted-foreground">Slammer — Evershade Dashboard</span>
          </div>

          {/* Top bar */}
          <div className="flex items-center justify-between border-b border-border px-6 py-3">
            <div className="flex items-center gap-4">
              <span className={`flex items-center gap-2 font-mono text-[11px] ${paused ? 'text-muted-foreground' : 'text-signal'}`}>
                <span className={`size-2 rounded-full ${paused ? 'bg-muted-foreground' : 'animate-pulse bg-signal'}`} aria-hidden="true" />
                {paused ? 'Paused' : 'Demo'}
              </span>
              <span className="font-mono text-[11px] text-muted-foreground">{stats.workersBusy}/{stats.workersTotal} workers busy</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleNewMission}
                className="flex items-center gap-1.5 rounded border border-border px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider hover:bg-foreground hover:text-background transition-colors"
              >
                <Play className="size-3" aria-hidden="true" />
                New mission
              </button>
              <button
                onClick={handlePauseAll}
                className="flex items-center gap-1.5 rounded border border-border px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider hover:bg-foreground hover:text-background transition-colors"
              >
                {paused ? <Play className="size-3" aria-hidden="true" /> : <Pause className="size-3" aria-hidden="true" />}
                {paused ? 'Resume' : 'Pause all'}
              </button>
            </div>
          </div>

          {/* Notification */}
          {notification && (
            <div className="flex items-center justify-between border-b border-border bg-signal/10 px-6 py-2">
              <span className="font-mono text-[11px] text-signal">{notification}</span>
              <button onClick={() => setNotification(null)} className="text-muted-foreground hover:text-foreground">
                <X className="size-3" />
              </button>
            </div>
          )}

          {/* Stats bar */}
          <div className="grid grid-cols-2 gap-px border-b border-border bg-border md:grid-cols-4">
            <StatItem label="Active missions" value={String(stats.activeMissions)} icon={Activity} />
            <StatItem label="Workers" value={`${stats.workersBusy}/${stats.workersTotal}`} icon={Terminal} />
            <StatItem label="Pending approvals" value={String(stats.pendingApprovals)} icon={Shield} />
            <StatItem label="Model cost today" value={`$${stats.modelCostToday.toFixed(2)}`} icon={BarChart3} />
          </div>

          {/* Tab navigation */}
          <div className="flex border-b border-border">
            {TABS.map((tab) => {
              const TabIcon = TAB_ICONS[tab]
              const count = tab === 'missions' ? missions.length : tab === 'agents' ? agents.length : approvals.length
              return (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex items-center gap-2 px-6 py-3 font-mono text-[11px] uppercase tracking-wider transition-colors ${
                    activeTab === tab
                      ? 'border-b-2 border-signal text-signal'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <TabIcon className="size-4" aria-hidden="true" />
                  {tab}
                  <span className="ml-1 rounded bg-foreground/10 px-1.5 py-0.5 text-[10px]">{count}</span>
                </button>
              )
            })}
          </div>

          {/* Tab content */}
          <div className="min-h-[200px]">
            {/* Missions tab */}
            {activeTab === 'missions' && (
              <div className="divide-y divide-border">
                {missions.map((mission) => (
                  <div key={mission.id}>
                    <button
                      onClick={() => toggleMission(mission.id)}
                      className="flex w-full items-center justify-between px-5 py-3 hover:bg-foreground/[0.02] transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        {expandedMission === mission.id ? (
                          <ChevronDown className="size-3 text-muted-foreground" />
                        ) : (
                          <ChevronRight className="size-3 text-muted-foreground" />
                        )}
                        <span className={`flex items-center gap-1.5 font-mono text-[11px] ${statusColor(mission.status)}`}>
                          {statusIcon(mission.status)}
                          {mission.id} · {mission.name}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        {mission.progress > 0 && mission.progress < 100 && (
                          <div className="flex items-center gap-2">
                            <div className="h-1.5 w-16 overflow-hidden rounded-full bg-border">
                              <div
                                className={`h-full rounded-full transition-all duration-500 ${mission.status === 'failed' ? 'bg-destructive' : 'bg-signal'}`}
                                style={{ width: `${mission.progress}%` }}
                              />
                            </div>
                            <span className="font-mono text-[10px] text-muted-foreground">{mission.progress}%</span>
                          </div>
                        )}
                        {mission.status === 'completed' && (
                          <span className="font-mono text-[10px] text-muted-foreground">Done</span>
                        )}
                        {mission.status === 'queued' && (
                          <span className="font-mono text-[10px] text-muted-foreground/60">Waiting</span>
                        )}
                        {mission.status === 'failed' && (
                          <span className="font-mono text-[10px] text-destructive">Failed</span>
                        )}
                      </div>
                    </button>
                    {expandedMission === mission.id && (
                      <div className="border-t border-border bg-foreground/[0.02] px-5 py-4">
                        <div className="grid grid-cols-2 gap-4 font-mono text-[11px] md:grid-cols-4">
                          <div>
                            <span className="text-muted-foreground">Milestones</span>
                            <p className="mt-1">{mission.currentMilestone}/{mission.milestones}</p>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Workers</span>
                            <p className="mt-1">{mission.workers.length > 0 ? mission.workers.join(', ') : 'None'}</p>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Started</span>
                            <p className="mt-1">{mission.startTime}</p>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Model cost</span>
                            <p className="mt-1">${mission.modelCost.toFixed(4)}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Agents tab */}
            {activeTab === 'agents' && (
              <div className="divide-y divide-border">
                {agents.map((agent) => (
                  <div key={agent.id} className="flex items-center justify-between px-5 py-3">
                    <div className="flex items-center gap-2">
                      <span className={`font-mono text-[11px] ${agent.status === 'running' ? 'text-signal' : 'text-muted-foreground/60'}`}>
                        {statusIcon(agent.status)}
                        {agent.id}
                      </span>
                      {agent.missionId && (
                        <span className="font-mono text-[10px] text-muted-foreground">→ {agent.missionId}</span>
                      )}
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="font-mono text-[10px] text-muted-foreground">{agent.container}</span>
                      <span className="font-mono text-[10px] text-muted-foreground">{agent.tasksCompleted} tasks</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Approvals tab */}
            {activeTab === 'approvals' && (
              <div className="divide-y divide-border">
                {approvals.length === 0 ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                      <CheckCircle className="mx-auto size-8 text-muted-foreground/40" />
                      <p className="mt-2 font-mono text-[11px] text-muted-foreground">No pending approvals</p>
                    </div>
                  </div>
                ) : (
                  approvals.map((approval) => (
                    <div key={approval.id} className="flex items-center justify-between px-5 py-3">
                      <div className="flex items-center gap-2">
                        <Shield className="size-3 text-muted-foreground/60" />
                        <span className="font-mono text-[11px]">{approval.action}</span>
                        <span className="font-mono text-[10px] text-muted-foreground">({approval.missionId})</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleApprove(approval.id, approval.action)}
                          className="flex items-center gap-1 rounded bg-signal/10 px-2 py-1 font-mono text-[10px] text-signal hover:bg-signal/20 transition-colors"
                        >
                          <CheckCircle className="size-3" />
                          Approve
                        </button>
                        <button
                          onClick={() => handleDeny(approval.id, approval.action)}
                          className="flex items-center gap-1 rounded bg-destructive/10 px-2 py-1 font-mono text-[10px] text-destructive hover:bg-destructive/20 transition-colors"
                        >
                          <X className="size-3" />
                          Deny
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Bottom log area */}
          <div className="border-t border-border">
            <div className="flex items-center justify-between border-b border-border px-5 py-2">
              <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Demo logs</span>
              <span className="flex items-center gap-2 font-mono text-[10px] text-muted-foreground/60">
                <span className={`size-1.5 rounded-full ${paused ? 'bg-muted-foreground' : 'animate-pulse bg-signal'}`} />
                SSE stream
              </span>
            </div>
            <div className="max-h-32 overflow-hidden bg-foreground/[0.02] p-4 font-mono text-[10px] leading-relaxed text-muted-foreground">
              {logs.map((log, i) => (
                <p key={i}>
                  <span className="text-muted-foreground/40">{log.timestamp}</span>{' '}
                  <span className="text-signal">{log.service}</span>{' '}
                  {log.message}
                </p>
              ))}
            </div>
          </div>
        </div>

        <p className="mt-4 font-mono text-[10px] text-muted-foreground">Slammer runs on port 5173. Accessible via browser or reverse proxy. SSE streaming for real-time updates.</p>
      </div>

      {/* Features list */}
      <div className="mt-16 grid gap-6 md:mt-24 md:grid-cols-3">
        {FEATURES.map((feature) => (
          <div key={feature.title} className="border-t border-foreground pt-6">
            <h3 className="text-lg font-semibold tracking-tight">{feature.title}</h3>
            <p className="mt-2 text-sm leading-snug text-muted-foreground">{feature.body}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
