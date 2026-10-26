// Diagnostics view — service health checks and integration status

import { useState, useEffect, useCallback } from 'react';
import { runDiagnostics, checkIntegrations } from '../lib/api';

export default function DiagnosticsView() {
  const [diagnostics, setDiagnostics] = useState<any[]>([]);
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  const runAll = useCallback(async () => {
    setLoading(true);
    setRunning(true);

    const [diagResults, integrationResults] = await Promise.all([
      runDiagnostics(),
      checkIntegrations(),
    ]);

    setDiagnostics(diagResults);
    setIntegrations(integrationResults);
    setRunning(false);
    setLoading(false);
  }, []);

  useEffect(() => {
    runAll();
  }, [runAll]);

  const statusIcon = (status: string) => {
    if (status === 'ok' || status === 'connected') return '✅';
    if (status === 'error' || status === 'disconnected') return '❌';
    return '⚠️';
  };

  const statusColor = (status: string) => {
    if (status === 'ok' || status === 'connected') return 'text-green-400';
    if (status === 'error' || status === 'disconnected') return 'text-red-400';
    return 'text-yellow-400';
  };

  const okCount = diagnostics.filter(d => d.status === 'ok').length;
  const totalCount = diagnostics.length;
  const connectedCount = integrations.filter(i => i.status === 'connected').length;
  const integrationTotal = integrations.length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Diagnostics</h2>
        <button
          onClick={runAll}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-md text-sm"
        >
          {running ? 'Running...' : '↻ Run Diagnostics'}
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-sm text-gray-400">Services</h3>
          <p className="text-3xl font-bold mt-1">
            <span className="text-green-400">{okCount}</span>
            <span className="text-gray-500">/{totalCount}</span>
          </p>
          <p className="text-xs text-gray-500 mt-1">Healthy</p>
        </div>
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-sm text-gray-400">Integrations</h3>
          <p className="text-3xl font-bold mt-1">
            <span className="text-green-400">{connectedCount}</span>
            <span className="text-gray-500">/{integrationTotal}</span>
          </p>
          <p className="text-xs text-gray-500 mt-1">Connected</p>
        </div>
      </div>

      {/* Service Diagnostics */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="font-semibold mb-4">Service Health</h3>
        {loading ? (
          <p className="text-gray-400">Checking services...</p>
        ) : diagnostics.length === 0 ? (
          <p className="text-gray-400">Click "Run Diagnostics" to check all services.</p>
        ) : (
          <div className="space-y-2">
            {diagnostics.map((diag) => (
              <div key={diag.service} className="flex items-center justify-between py-3 border-b border-gray-700 last:border-0">
                <div className="flex items-center gap-3">
                  <span>{statusIcon(diag.status)}</span>
                  <div>
                    <div className="font-medium">{diag.service}</div>
                    <div className="text-xs text-gray-500">{diag.endpoint}</div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {diag.error && (
                    <span className="text-xs text-red-400">{diag.error}</span>
                  )}
                  <span className={`text-sm ${statusColor(diag.status)}`}>
                    {diag.latency}ms
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Integration Status */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="font-semibold mb-4">Integration Status</h3>
        {loading ? (
          <p className="text-gray-400">Checking integrations...</p>
        ) : integrations.length === 0 ? (
          <p className="text-gray-400">No integrations to check.</p>
        ) : (
          <div className="space-y-2">
            {integrations.map((integration) => (
              <div key={integration.name} className="flex items-center justify-between py-3 border-b border-gray-700 last:border-0">
                <div className="flex items-center gap-3">
                  <span>{statusIcon(integration.status)}</span>
                  <div>
                    <div className="font-medium">{integration.name}</div>
                    <div className="text-xs text-gray-500">{integration.type}</div>
                  </div>
                </div>
                <span className={`text-sm ${statusColor(integration.status)}`}>
                  {integration.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Troubleshooting */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="font-semibold mb-4">Troubleshooting</h3>
        <div className="space-y-3 text-sm">
          <div className="p-3 bg-gray-900 rounded-lg">
            <h4 className="font-medium text-yellow-400">⚠️ Service Unreachable</h4>
            <p className="text-gray-400 mt-1">Check if the service container is running: <code className="bg-gray-800 px-1 rounded">docker ps</code></p>
          </div>
          <div className="p-3 bg-gray-900 rounded-lg">
            <h4 className="font-medium text-yellow-400">⚠️ High Latency</h4>
            <p className="text-gray-400 mt-1">Check resource usage in Grafana or run <code className="bg-gray-800 px-1 rounded">evershade monitoring status</code></p>
          </div>
          <div className="p-3 bg-gray-900 rounded-lg">
            <h4 className="font-medium text-yellow-400">⚠️ Integration Disconnected</h4>
            <p className="text-gray-400 mt-1">Optional integrations require specific Docker Compose profiles. Check docs/INTEGRATION_SETUP.md</p>
          </div>
        </div>
      </div>
    </div>
  );
}
