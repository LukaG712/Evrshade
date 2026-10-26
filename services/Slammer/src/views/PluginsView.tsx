// Plugins view — manage integrations and plugins

import { useState, useEffect } from 'react';
import { api } from '../lib/api';

const defaultPlugins = [
  { name: 'OpenTelemetry', description: 'Distributed tracing and metrics', status: 'active', version: '1.0' },
  { name: 'Opik', description: 'LLM observability and evaluation', status: 'optional', version: '1.0' },
  { name: 'Prometheus', description: 'Metrics collection and alerting', status: 'active', version: '2.0' },
  { name: 'Grafana', description: 'Metrics visualization dashboards', status: 'active', version: '2.0' },
  { name: 'Playwright', description: 'Browser automation backend', status: 'active', version: '1.0' },
  { name: 'SQLite', description: 'Default database for all services', status: 'active', version: '3.x' },
];

export default function PluginsView() {
  const [plugins, setPlugins] = useState(defaultPlugins);
  const [providers, setProviders] = useState<any[]>([]);
  const [channels, setChannels] = useState<any[]>([]);

  useEffect(() => {
    api.getProviders()
      .then((data) => setProviders(data.providers || []))
      .catch(() => {});

    api.getChannels()
      .then((data) => setChannels(data.channels || []))
      .catch(() => {});
  }, []);

  const statusColor = (status: string) =>
    status === 'active' ? 'text-green-400' :
    status === 'optional' ? 'text-yellow-400' :
    'text-gray-400';

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Plugins & Integrations</h2>

      {/* Core plugins */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="font-semibold mb-4">Core Integrations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plugins.map((plugin) => (
            <div key={plugin.name} className="bg-gray-900 rounded-lg p-4 border border-gray-700">
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-medium">{plugin.name}</h4>
                  <p className="text-sm text-gray-400 mt-1">{plugin.description}</p>
                </div>
                <span className={`text-xs ${statusColor(plugin.status)}`}>{plugin.status}</span>
              </div>
              <p className="text-xs text-gray-500 mt-3">v{plugin.version}</p>
            </div>
          ))}
        </div>
      </div>

      {/* LLM Providers */}
      {providers.length > 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="font-semibold mb-4">LLM Providers (Shrewd)</h3>
          <div className="space-y-2">
            {providers.map((p: any) => (
              <div key={p.id} className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0">
                <span>{p.name}</span>
                <span className="text-sm text-gray-400">{p.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Notification Channels */}
      {channels.length > 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="font-semibold mb-4">Notification Channels (Poltergeist)</h3>
          <div className="space-y-2">
            {channels.map((c: any) => (
              <div key={c.id} className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0">
                <div>
                  <span>{c.name}</span>
                  <span className="text-xs text-gray-500 ml-2">({c.type})</span>
                </div>
                <span className={`text-xs ${c.enabled ? 'text-green-400' : 'text-gray-500'}`}>
                  {c.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
