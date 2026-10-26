// Shared types for the Evershade dashboard

export interface ServiceStatus {
  name: string;
  port: number;
  status: 'healthy' | 'unhealthy' | 'pending' | 'unknown';
  version?: string;
  uptime?: string;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'idle' | 'error' | 'stopped';
  model?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Mission {
  id: string;
  name: string;
  status: 'planning' | 'executing' | 'validating' | 'completed' | 'failed' | 'paused';
  agentId?: string;
  progress: number;
  milestones: Milestone[];
  createdAt: string;
  updatedAt: string;
}

export interface Milestone {
  id: string;
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  description?: string;
}

export interface LogEntry {
  id: string;
  service: string;
  level: 'debug' | 'info' | 'warn' | 'error' | 'critical';
  message: string;
  timestamp: string;
  traceId?: string;
}

export interface MetricPoint {
  name: string;
  value: number;
  timestamp: string;
  labels?: Record<string, string>;
}

export interface Task {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  worker?: string;
  progress: number;
  createdAt: string;
  completedAt?: string;
}

export interface NotificationChannel {
  id: string;
  type: 'slack' | 'discord' | 'email' | 'telegram';
  name: string;
  enabled: boolean;
  config: Record<string, string>;
}

export interface DashboardStats {
  totalAgents: number;
  activeAgents: number;
  totalMissions: number;
  activeMissions: number;
  totalTasks: number;
  runningTasks: number;
  servicesHealthy: number;
  servicesTotal: number;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'paused' | 'disabled';
  runs?: number;
  lastRun?: string;
  createdAt: string;
}

export interface WorkflowRun {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  triggerType: string;
  startedAt?: string;
  completedAt?: string;
  error?: string;
}

export interface ModelProvider {
  id: string;
  name: string;
  baseUrl: string;
  enabled: boolean;
  models: string[];
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  capabilities: string[];
  contextWindow: number;
  costPerToken?: number;
}

export interface KnowledgeEntry {
  id: string;
  title: string;
  content: string;
  source?: string;
  tags: string[];
  createdAt: string;
}

export interface NotificationRule {
  id: string;
  name: string;
  event: string;
  channel: string;
  enabled: boolean;
  condition?: string;
}

export interface DiagnosticInfo {
  service: string;
  endpoint: string;
  status: 'ok' | 'error' | 'unreachable';
  latency: number;
  error?: string;
}

export interface IntegrationStatus {
  name: string;
  type: string;
  enabled: boolean;
  status: 'connected' | 'disconnected' | 'configuring';
  endpoint?: string;
}
