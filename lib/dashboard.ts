export type MissionStatus = 'running' | 'queued' | 'completed' | 'failed'

export type Mission = {
  id: string
  name: string
  status: MissionStatus
  progress: number
  milestones: number
  currentMilestone: number
  workers: string[]
  startTime: string
  modelCost: number
}

export type Agent = {
  id: string
  missionId: string | null
  status: 'running' | 'idle'
  container: string
  tasksCompleted: number
}

export type Approval = {
  id: string
  action: string
  missionId: string
  sensitive: boolean
  timestamp: string
}

export type LogEntry = {
  timestamp: string
  service: string
  message: string
}

export type DashboardData = {
  missions: Mission[]
  agents: Agent[]
  approvals: Approval[]
  logs: LogEntry[]
  stats: {
    activeMissions: number
    workersBusy: number
    workersTotal: number
    pendingApprovals: number
    modelCostToday: number
  }
}

// Simulated initial data
export function generateInitialData(): DashboardData {
  return {
    missions: [
      {
        id: 'm_7f3a',
        name: 'Add rate limiting',
        status: 'running',
        progress: 67,
        milestones: 3,
        currentMilestone: 2,
        workers: ['worker-1'],
        startTime: '14:05:00',
        modelCost: 0.012,
      },
      {
        id: 'm_2e91',
        name: 'Update dependencies',
        status: 'queued',
        progress: 0,
        milestones: 2,
        currentMilestone: 0,
        workers: [],
        startTime: '-',
        modelCost: 0,
      },
      {
        id: 'm_4b1c',
        name: 'Refactor auth module',
        status: 'completed',
        progress: 100,
        milestones: 4,
        currentMilestone: 4,
        workers: [],
        startTime: '13:30:00',
        modelCost: 0.028,
      },
      {
        id: 'm_8d5f',
        name: 'Fix login timeout',
        status: 'failed',
        progress: 42,
        milestones: 2,
        currentMilestone: 1,
        workers: [],
        startTime: '13:45:00',
        modelCost: 0.005,
      },
    ],
    agents: [
      { id: 'worker-1', missionId: 'm_7f3a', status: 'running', container: 'alpine:3.20', tasksCompleted: 12 },
      { id: 'worker-2', missionId: null, status: 'idle', container: 'alpine:3.20', tasksCompleted: 8 },
      { id: 'worker-3', missionId: null, status: 'idle', container: 'alpine:3.20', tasksCompleted: 5 },
    ],
    approvals: [
      { id: 'a_1', action: 'Install express@5.0', missionId: 'm_7f3a', sensitive: true, timestamp: '14:07:20' },
      { id: 'a_2', action: 'Push to main branch', missionId: 'm_7f3a', sensitive: true, timestamp: '14:07:22' },
    ],
    logs: [
      { timestamp: '14:07:23', service: 'greenie', message: 'mission m_7f3a · milestone 2/3 · feature "add middleware" started' },
      { timestamp: '14:07:24', service: 'slinker', message: 'worker-1 · container created · alpine:3.20' },
      { timestamp: '14:07:25', service: 'shrewd', message: 'route → planner model · cost $0.0012' },
      { timestamp: '14:07:28', service: 'slinker', message: 'worker-1 · pytest -q · 12 passed in 2.4s' },
      { timestamp: '14:07:30', service: 'hider', message: 'lease GITHUB_TOKEN · aes-256-gcm · ok' },
    ],
    stats: {
      activeMissions: 1,
      workersBusy: 1,
      workersTotal: 3,
      pendingApprovals: 2,
      modelCostToday: 0.04,
    },
  }
}
