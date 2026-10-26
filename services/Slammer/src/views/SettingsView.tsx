// Settings view — platform configuration

import { useState, useEffect } from 'react';
import { api } from '../lib/api';

export default function SettingsView() {
  const [config, setConfig] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getConfig()
      .then((data) => {
        const map: Record<string, any> = {};
        (data.config || []).forEach((c: any) => { map[c.key] = c; });
        setConfig(map);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleUpdate = async (key: string, value: string) => {
    try {
      await api.updateConfig(key, { value });
      setConfig(prev => ({ ...prev, [key]: { ...prev[key], value } }));
    } catch (err: any) {
      alert(`Failed to update: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Settings</h2>

      {/* Platform info */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="font-semibold mb-4">Platform Information</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400">Version:</span>
            <span className="ml-2">v2.0.0</span>
          </div>
          <div>
            <span className="text-gray-400">Services:</span>
            <span className="ml-2">10</span>
          </div>
          <div>
            <span className="text-gray-400">Database:</span>
            <span className="ml-2">SQLite (WAL)</span>
          </div>
          <div>
            <span className="text-gray-400">Network:</span>
            <span className="ml-2">Docker Compose</span>
          </div>
        </div>
      </div>

      {/* External services */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="font-semibold mb-4">External Services</h3>
        <div className="space-y-3">
          <a href="/grafana" target="_blank" rel="noopener noreferrer"
            className="block p-4 bg-gray-900 rounded-lg border border-gray-700 hover:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Grafana</h4>
                <p className="text-sm text-gray-400">Metrics dashboards</p>
              </div>
              <span className="text-gray-400">→</span>
            </div>
          </a>
          <a href="/prometheus" target="_blank" rel="noopener noreferrer"
            className="block p-4 bg-gray-900 rounded-lg border border-gray-700 hover:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Prometheus</h4>
                <p className="text-sm text-gray-400">Metrics query interface</p>
              </div>
              <span className="text-gray-400">→</span>
            </div>
          </a>
          <a href="/opik" target="_blank" rel="noopener noreferrer"
            className="block p-4 bg-gray-900 rounded-lg border border-gray-700 hover:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Opik</h4>
                <p className="text-sm text-gray-400">LLM observability</p>
              </div>
              <span className="text-gray-400">→</span>
            </div>
          </a>
        </div>
      </div>

      {/* Configuration */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="font-semibold mb-4">Configuration</h3>
        {loading ? (
          <p className="text-gray-400">Loading...</p>
        ) : error ? (
          <p className="text-red-400">{error}</p>
        ) : Object.keys(config).length === 0 ? (
          <p className="text-gray-400">No configuration entries.</p>
        ) : (
          <div className="space-y-3">
            {Object.entries(config).map(([key, entry]: [string, any]) => (
              <div key={key} className="flex items-center gap-3">
                <span className="text-sm text-gray-400 w-48 truncate">{key}</span>
                <input
                  type="text"
                  defaultValue={entry?.value || ''}
                  onBlur={(e) => handleUpdate(key, e.target.value)}
                  className="flex-1 bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-sm"
                />
                {entry?.version && (
                  <span className="text-xs text-gray-500">v{entry.version}</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Secrets */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="font-semibold mb-4">Secrets (Hider)</h3>
        <p className="text-sm text-gray-400">
          Secrets are encrypted at rest using AES-256-GCM. Manage them via the API or CLI.
        </p>
        <div className="mt-3">
          <code className="bg-gray-900 px-2 py-1 rounded text-sm">
            evershade config secrets list
          </code>
        </div>
      </div>
    </div>
  );
}
