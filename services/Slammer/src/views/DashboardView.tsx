// Dashboard overview view — real-time service and task data

import { useState, useEffect, useCallback } from 'react';
import { api, runDiagnostics, checkIntegrations } from '../lib/api';

function StatCard({ title, value, subtitle, icon }: { title: string; value: string | number; subtitle?: string; icon: string }) {
  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-3xl font-bold mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <span className="text-4xl">{icon}</span>
      </div>
    </div>
  );
}

function ServiceRow({ name, status, port }: { name: string; status: string; port: number }) {
  const color =
    status === 'healthy' || status === 'registered' ? 'text-green-400' :
    status === 'unhealthy' ? 'text-red-400' :
    'text-yellow-400';

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0">
      <div className="flex items-center gap-3">
        <span className={`w-2 h-2 rounded-full ${status === 'healthy' || status === 'registered' ? 'bg-green-400' : status === 'unhealthy' ? 'bg-red-400' : 'bg-yellow-400'}`} />
        <span className="font-medium">{name}</span>
      </div>
      <div className="flex items-center gap-4 text-sm text-gray-400">
        <span className={color}>{status}</span>
        <span>:{port}</span>
      </div>
    </div>
  );
}

function IntegrationRow({ name, type, status }: { name: string; type: string; status: string }) {
  const color = status === 'connected' ? 'text-green-400' : status === 'configuring' ? 'text-yellow-400' : 'text-gray-500';

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0">
      <div className="flex items-center gap-3">
        <span className={`w-2 h-2 rounded-full ${status === 'connected' ? 'bg-green-400' : status === 'configuring' ? 'bg-yellow-400' : 'bg-gray-500'}`} />
        <div>
          <span className="font-medium">{name}</span>
          <span className="text-xs text-gray-500 ml-2">{type}</span>
        </div>
      </div>
      <span className={`text-sm ${color}`}>{status}</span>
    </div>
  );
}

const defaultServices = [
  { name: 'Greenie', status: 'pending', port: 8080 },
  { name: 'Slinker', status: 'pending', port: 8000 },
  { name: 'Trapper', status: 'pending', port: 3000 },
  { name: 'Gobber', status: 'pending', port: 8085 },
  { name: 'Sneaker', status: 'pending', port: 8086 },
  { name: 'Hider', status: 'pending', port: 8087 },
  { name: 'Poltergeist', status: 'pending', port: 8088 },
  { name: 'Shrewd', status: 'pending', port: 8089 },
  { name: 'Slammer', status: 'healthy', port: 5173 },
];

export default function DashboardView() {
  const [services, setServices] = useState(defaultServices);
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    agents: { total: 0, active: 0 },
    missions: { total: 0, active: 0 },
    tasks: { total: 0, running: 0 },
  });

  const fetchData = useCallback(async () => {
    // Fetch service registry
    try {
      const registry = await api.getRegistry();
      if (registry.services) {
        setServices(prev => prev.map(s => {
          const found = registry.services.find((r: any) => r.name === s.name);
          return found ? { ...s, status: found.status || 'registered' } : s;
        }));
      }
    } catch {
      // Fallback: check individual health
      try {
        const health = await api.getHealth();
        setServices(prev => prev.map(s =>
          s.name === 'Greenie' ? { ...s, status: 'healthy' } : s
        ));
      } catch {}
    }

    // Fetch agents
    try {
      const agents = await api.getAgents();
      if (agents.agents) {
        const total = agents.agents.length;
        const active = agents.agents.filter((a: any) => a.status === 'active').length;
        setStats(prev => ({ ...prev, agents: { total, active } }));
      }
    } catch {}

    // Fetch missions
    try {
      const missions = await api.getMissions();
      if (missions.missions) {
        const total = missions.missions.length;
        const active = missions.missions.filter((m: any) => ['planning', 'executing', 'validating'].includes(m.status)).length;
        setStats(prev => ({ ...prev, missions: { total, active } }));
      }
    } catch {}

    // Fetch tasks
    try {
      const tasks = await api.getTasks();
      if (tasks.tasks) {
        const total = tasks.tasks.length;
        const running = tasks.tasks.filter((t: any) => t.status === 'running').length;
        setStats(prev => ({ ...prev, tasks: { total, running } }));
      }
    } catch {}

    // Fetch integrations
    try {
      const integrationsData = await checkIntegrations();
      setIntegrations(integrationsData);
    } catch {}

    setLoading(false);
  }, []);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const healthyCount = services.filter(s => s.status === 'healthy' || s.status === 'registered').length;
  const connectedIntegrations = integrations.filter(i => i.status === 'connected').length;

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Services" value={`${healthyCount}/${services.length}`} subtitle="Healthy" icon="🖥️" />
        <StatCard title="Agents" value={`${stats.agents.active}/${stats.agents.total}`} subtitle="Active" icon="🤖" />
        <StatCard title="Missions" value={`${stats.missions.active}/${stats.missions.total}`} subtitle="In Progress" icon="🎯" />
        <StatCard title="Tasks" value={`${stats.tasks.running}/${stats.tasks.total}`} subtitle="Running" icon="⚡" />
      </div>

      {/* Services */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Service Status</h2>
          <button onClick={fetchData} className="text-sm text-blue-400 hover:text-blue-300">
            ↻ Refresh
          </button>
        </div>
        {loading ? (
          <p className="text-gray-400">Loading...</p>
        ) : (
          <div className="space-y-1">
            {services.map((s) => (
              <ServiceRow key={s.name} name={s.name} status={s.status} port={s.port} />
            ))}
          </div>
        )}
      </div>

      {/* Integrations */}
      {integrations.length > 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-lg font-semibold mb-4">
            Integrations <span className="text-sm text-gray-400">({connectedIntegrations}/{integrations.length} connected)</span>
          </h2>
          <div className="space-y-1">
            {integrations.map((i) => (
              <IntegrationRow key={i.name} name={i.name} type={i.type} status={i.status} />
            ))}
          </div>
        </div>
      )}

      {/* Quick links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a href="/grafana" target="_blank" rel="noopener noreferrer"
          className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-gray-600 transition-colors">
          <h3 className="font-semibold">📈 Grafana</h3>
          <p className="text-sm text-gray-400 mt-1">View metrics and dashboards</p>
        </a>
        <a href="/prometheus" target="_blank" rel="noopener noreferrer"
          className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-gray-600 transition-colors">
          <h3 className="font-semibold">🔍 Prometheus</h3>
          <p className="text-sm text-gray-400 mt-1">Query metrics data</p>
        </a>
        <a href="/opik" target="_blank" rel="noopener noreferrer"
          className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-gray-600 transition-colors">
          <h3 className="font-semibold">🧠 Opik</h3>
          <p className="text-sm text-gray-400 mt-1">LLM observability</p>
        </a>
      </div>
    </div>
  );
}
