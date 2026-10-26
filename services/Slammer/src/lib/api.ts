// API client for communicating with Evershade services

const API_BASE = '/api';

interface FetchOptions extends RequestInit {
  timeout?: number;
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { timeout = 30000, ...fetchOptions } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...fetchOptions,
      headers: {
        'Content-Type': 'application/json',
        ...fetchOptions.headers,
      },
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorBody = await response.text().catch(() => '');
      throw new Error(`API error ${response.status}: ${errorBody || response.statusText}`);
    }

    const text = await response.text();
    if (!text) return {} as T;
    return JSON.parse(text);
  } finally {
    clearTimeout(timeoutId);
  }
}

export const api = {
  // Health & status
  getHealth: () => apiFetch<{ status: string; version: string }>('/status'),
  getCapabilities: () => apiFetch<{ capabilities: string[] }>('/capabilities'),

  // Services
  getServices: () => apiFetch<{ services: Array<{ name: string; status: string; port: number }> }>('/services'),

  // Agents
  getAgents: () => apiFetch<{ agents: Array<{ id: string; name: string; description: string; status: string; model?: string; createdAt: string; updatedAt: string }> }>('/agents'),
  getAgent: (id: string) => apiFetch<unknown>(`/agents/${id}`),
  createAgent: (data: unknown) => apiFetch<unknown>('/agents', { method: 'POST', body: JSON.stringify(data) }),
  updateAgent: (id: string, data: unknown) => apiFetch<unknown>(`/agents/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteAgent: (id: string) => apiFetch<unknown>(`/agents/${id}`, { method: 'DELETE' }),

  // Missions
  getMissions: () => apiFetch<{ missions: Array<{ id: string; name: string; status: string; progress: number; milestones: unknown[]; createdAt: string; updatedAt: string }> }>('/missions'),
  getMission: (id: string) => apiFetch<unknown>(`/missions/${id}`),
  createMission: (data: unknown) => apiFetch<unknown>('/missions', { method: 'POST', body: JSON.stringify(data) }),
  updateMission: (id: string, data: unknown) => apiFetch<unknown>(`/missions/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  // Chat
  getChatSessions: () => apiFetch<{ sessions: unknown[] }>('/chat/sessions'),
  getChatMessages: (sessionId: string) => apiFetch<{ messages: unknown[] }>(`/chat/sessions/${sessionId}/messages`),
  sendChatMessage: (sessionId: string, data: unknown) =>
    apiFetch<unknown>(`/chat/sessions/${sessionId}/messages`, { method: 'POST', body: JSON.stringify(data) }),

  // Tasks (Slinker)
  getTasks: () => apiFetch<{ tasks: unknown[] }>('/v1/tasks'),
  getTask: (id: string) => apiFetch<unknown>(`/v1/tasks/${id}`),
  createTask: (data: unknown) => apiFetch<unknown>('/v1/tasks', { method: 'POST', body: JSON.stringify(data) }),

  // Workers
  getWorkers: () => apiFetch<{ workers: unknown[] }>('/v1/workers'),

  // Logs (Sneaker)
  getLogs: (params?: { service?: string; level?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.service) qs.set('service', params.service);
    if (params?.level) qs.set('level', params.level);
    if (params?.limit) qs.set('limit', String(params.limit));
    const query = qs.toString();
    return apiFetch<{ logs: unknown[] }>(`/logs${query ? '?' + query : ''}`);
  },

  // Metrics (Sneaker)
  getMetrics: (params?: { name?: string; service?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.name) qs.set('name', params.name);
    if (params?.service) qs.set('service', params.service);
    if (params?.limit) qs.set('limit', String(params.limit));
    const query = qs.toString();
    return apiFetch<{ metrics: unknown[] }>(`/metrics${query ? '?' + query : ''}`);
  },

  // Traces (Sneaker)
  getTraces: (params?: { traceId?: string; service?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.traceId) qs.set('trace_id', params.traceId);
    if (params?.service) qs.set('service', params.service);
    if (params?.limit) qs.set('limit', String(params.limit));
    const query = qs.toString();
    return apiFetch<{ traces: unknown[] }>(`/traces${query ? '?' + query : ''}`);
  },

  // Secrets (Hider)
  getSecrets: () => apiFetch<{ secrets: Array<{ id: string; key: string; version: number }> }>('/secrets'),
  createSecret: (data: unknown) => apiFetch<unknown>('/secrets', { method: 'POST', body: JSON.stringify(data) }),
  deleteSecret: (id: string) => apiFetch<unknown>(`/secrets/${id}`, { method: 'DELETE' }),

  // Config (Hider)
  getConfig: () => apiFetch<{ config: unknown[] }>('/config/all'),
  getConfigEntry: (key: string) => apiFetch<unknown>(`/config/${key}`),
  updateConfig: (key: string, data: unknown) => apiFetch<unknown>(`/config/${key}`, { method: 'PUT', body: JSON.stringify(data) }),

  // Notifications (Poltergeist)
  getChannels: () => apiFetch<{ channels: unknown[] }>('/channels'),
  createChannel: (data: unknown) => apiFetch<unknown>('/channels', { method: 'POST', body: JSON.stringify(data) }),
  sendNotification: (data: unknown) => apiFetch<unknown>('/notifications', { method: 'POST', body: JSON.stringify(data) }),

  // Knowledge (Gobber)
  getNotes: () => apiFetch<{ notes: unknown[] }>('/notes'),
  searchKnowledge: (query: string) => apiFetch<{ results: unknown[] }>(`/embeddings/search?q=${encodeURIComponent(query)}`),

  // LLM (Shrewd)
  getProviders: () => apiFetch<{ providers: unknown[] }>('/providers'),
  getModels: () => apiFetch<{ models: unknown[] }>('/models'),
  chatCompletion: (data: unknown) => apiFetch<unknown>('/chat/completions', { method: 'POST', body: JSON.stringify(data) }),

  // Browser (Trapper)
  scrapeUrl: (url: string, options?: unknown) =>
    apiFetch<unknown>('/scrape', { method: 'POST', body: JSON.stringify({ url, ...options }) }),

  // Workflows (Greenie)
  getWorkflows: () => apiFetch<{ workflows: Array<{ id: string; name: string; description: string; status: string; runs?: number; lastRun?: string; createdAt: string }> }>('/workflows'),
  getWorkflow: (id: string) => apiFetch<unknown>(`/workflows/${id}`),
  createWorkflow: (data: unknown) => apiFetch<unknown>('/workflows', { method: 'POST', body: JSON.stringify(data) }),
  updateWorkflow: (id: string, data: unknown) => apiFetch<unknown>(`/workflows/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteWorkflow: (id: string) => apiFetch<unknown>(`/workflows/${id}`, { method: 'DELETE' }),
  executeWorkflow: (id: string, data?: unknown) => apiFetch<unknown>(`/workflows/${id}/execute`, { method: 'POST', body: data ? JSON.stringify(data) : undefined }),
  getWorkflowRuns: (id: string) => apiFetch<{ runs: Array<{ id: string; status: string; triggerType: string; startedAt?: string; completedAt?: string; error?: string }> }>(`/workflows/${id}/runs`),

  // Registry (Greenie)
  getRegistry: () => apiFetch<{ services: Array<{ name: string; status: string; port: number; lastHeartbeat?: string }> }>('/registry'),

  // Knowledge search (Gobber)
  searchKnowledge: (query: string) => apiFetch<{ results: Array<{ id: string; title: string; content: string; source?: string; tags: string[]; score?: number }> }>(`/embeddings/search?q=${encodeURIComponent(query)}`),
  getMemory: (params?: { userId?: string; projectId?: string; agentId?: string }) => {
    const qs = new URLSearchParams();
    if (params?.userId) qs.set('user_id', params.userId);
    if (params?.projectId) qs.set('project_id', params.projectId);
    if (params?.agentId) qs.set('agent_id', params.agentId);
    const query = qs.toString();
    return apiFetch<{ entries: Array<{ id: string; title: string; content: string; source?: string; tags: string[]; createdAt: string }> }>(`/memory${query ? '?' + query : ''}`);
  },

  // Model providers (Shrewd)
  getModelProviders: () => apiFetch<{ providers: Array<{ id: string; name: string; baseUrl: string; enabled: boolean; models: string[] }> }>('/providers'),
  getModelInfo: () => apiFetch<{ models: Array<{ id: string; name: string; provider: string; capabilities: string[]; contextWindow: number; costPerToken?: number }> }>('/models'),
  getUsageStats: () => apiFetch<{ stats: Array<{ model: string; requests: number; tokens: number; cost: number; avgLatency: number }> }>('/usage/stats'),

  // Notification rules (Poltergeist)
  getNotificationRules: () => apiFetch<{ rules: Array<{ id: string; name: string; event: string; channel: string; enabled: boolean; condition?: string }> }>('/notification-rules'),
  createNotificationRule: (data: unknown) => apiFetch<unknown>('/notification-rules', { method: 'POST', body: JSON.stringify(data) }),
  updateNotificationRule: (id: string, data: unknown) => apiFetch<unknown>(`/notification-rules/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteNotificationRule: (id: string) => apiFetch<unknown>(`/notification-rules/${id}`, { method: 'DELETE' }),

  // Diagnostics
  getDiagnostics: () => Promise<Array<{ service: string; endpoint: string; status: 'ok' | 'error' | 'unreachable'; latency: number; error?: string }>>,

  // Integrations status
  getIntegrations: () => Promise<Array<{ name: string; type: string; enabled: boolean; status: 'connected' | 'disconnected' | 'configuring'; endpoint?: string }>>,
};

// SSE connection for real-time mission logs
export function createMissionLogStream(missionId: string, onMessage: (data: string) => void) {
  const eventSource = new EventSource(`${API_BASE}/sse/logs/${missionId}`);
  eventSource.onmessage = (event) => onMessage(event.data);
  eventSource.onerror = () => {
    eventSource.close();
  };
  return () => eventSource.close();
}

// WebSocket connection for real-time feed
export function createWebSocketFeed(onOpen: () => void, onMessage: (data: string) => void, onClose: () => void) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws/feed`);
  ws.onopen = onOpen;
  ws.onmessage = (event) => onMessage(event.data);
  ws.onclose = onClose;
  return ws;
}

// Check Grafana health
export async function checkGrafanaHealth(): Promise<boolean> {
  try {
    const response = await fetch('/grafana-health', { signal: AbortSignal.timeout(3000) });
    return response.ok;
  } catch {
    return false;
  }
}

// Diagnostics — check all service endpoints
export async function runDiagnostics(): Promise<Array<{ service: string; endpoint: string; status: 'ok' | 'error' | 'unreachable'; latency: number; error?: string }>> {
  const services = [
    { service: 'Greenie', endpoint: '/api/status' },
    { service: 'Slinker', endpoint: '/api/v1/tasks' },
    { service: 'Trapper', endpoint: '/health' },
    { service: 'Gobber', endpoint: '/api/notes' },
    { service: 'Sneaker', endpoint: '/api/logs' },
    { service: 'Hider', endpoint: '/api/secrets' },
    { service: 'Poltergeist', endpoint: '/api/channels' },
    { service: 'Shrewd', endpoint: '/api/providers' },
  ];

  const results: Array<{ service: string; endpoint: string; status: 'ok' | 'error' | 'unreachable'; latency: number; error?: string }> = [];

  for (const svc of services) {
    const start = performance.now();
    try {
      const response = await fetch(`${API_BASE}${svc.endpoint}`, { signal: AbortSignal.timeout(5000) });
      const latency = Math.round(performance.now() - start);
      results.push({
        service: svc.service,
        endpoint: svc.endpoint,
        status: response.ok ? 'ok' : 'error',
        latency,
        error: response.ok ? undefined : `HTTP ${response.status}`,
      });
    } catch (err: any) {
      const latency = Math.round(performance.now() - start);
      results.push({
        service: svc.service,
        endpoint: svc.endpoint,
        status: 'unreachable',
        latency,
        error: err.message || 'Timeout',
      });
    }
  }

  return results;
}

// Integrations status — check optional integrations
export async function checkIntegrations(): Promise<Array<{ name: string; type: string; enabled: boolean; status: 'connected' | 'disconnected' | 'configuring'; endpoint?: string }>> {
  const integrations: Array<{ name: string; type: string; endpoint: string }> = [
    { name: 'Prometheus', type: 'monitoring', endpoint: '/prometheus' },
    { name: 'Grafana', type: 'monitoring', endpoint: '/grafana-health' },
    { name: 'Opik', type: 'ai-observability', endpoint: '/opik' },
    { name: 'Langfuse', type: 'ai-observability', endpoint: '/langfuse' },
    { name: 'Loki', type: 'log-aggregation', endpoint: '/loki' },
    { name: 'Tempo', type: 'tracing', endpoint: '/tempo' },
  ];

  const results: Array<{ name: string; type: string; enabled: boolean; status: 'connected' | 'disconnected' | 'configuring'; endpoint?: string }> = [];

  for (const integration of integrations) {
    try {
      const response = await fetch(integration.endpoint, { signal: AbortSignal.timeout(3000) });
      results.push({
        name: integration.name,
        type: integration.type,
        enabled: true,
        status: response.ok ? 'connected' : 'disconnected',
        endpoint: integration.endpoint,
      });
    } catch {
      results.push({
        name: integration.name,
        type: integration.type,
        enabled: false,
        status: 'disconnected',
        endpoint: integration.endpoint,
      });
    }
  }

  return results;
}
