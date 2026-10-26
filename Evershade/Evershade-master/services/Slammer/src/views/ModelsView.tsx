// Models view — model providers, models, and usage statistics

import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';

export default function ModelsView() {
  const [providers, setProviders] = useState<any[]>([]);
  const [models, setModels] = useState<any[]>([]);
  const [usageStats, setUsageStats] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [providersData, modelsData, usageData] = await Promise.allSettled([
        api.getModelProviders(),
        api.getModelInfo(),
        api.getUsageStats(),
      ]);

      if (providersData.status === 'fulfilled') {
        setProviders(providersData.value.providers || []);
      }
      if (modelsData.status === 'fulfilled') {
        setModels(modelsData.value.models || []);
      }
      if (usageData.status === 'fulfilled') {
        setUsageStats(usageData.value.stats || []);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Model Providers</h2>
        <button onClick={fetchData} className="text-sm text-blue-400 hover:text-blue-300">
          ↻ Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-4 text-red-300">✕</button>
        </div>
      )}

      {loading ? (
        <p className="text-gray-400">Loading providers...</p>
      ) : (
        <>
          {/* Providers */}
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h3 className="font-semibold mb-4">Providers ({providers.length})</h3>
            {providers.length === 0 ? (
              <p className="text-gray-400 text-sm">No providers configured. Add providers through the Shrewd API.</p>
            ) : (
              <div className="space-y-3">
                {providers.map((provider) => (
                  <div key={provider.id} className="flex items-center justify-between py-3 border-b border-gray-700 last:border-0">
                    <div>
                      <div className="font-medium flex items-center gap-2">
                        {provider.name}
                        {provider.enabled ? (
                          <span className="text-xs text-green-400">● Enabled</span>
                        ) : (
                          <span className="text-xs text-gray-500">○ Disabled</span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{provider.baseUrl}</p>
                    </div>
                    <div className="text-sm text-gray-400">
                      {provider.models?.length || 0} models
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Models */}
          {models.length > 0 && (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="font-semibold mb-4">Models ({models.length})</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left px-4 py-2 text-gray-400">Name</th>
                      <th className="text-left px-4 py-2 text-gray-400">Provider</th>
                      <th className="text-left px-4 py-2 text-gray-400">Capabilities</th>
                      <th className="text-left px-4 py-2 text-gray-400">Context</th>
                      <th className="text-left px-4 py-2 text-gray-400">Cost/Token</th>
                    </tr>
                  </thead>
                  <tbody>
                    {models.map((model) => (
                      <tr key={model.id} className="border-b border-gray-700 last:border-0">
                        <td className="px-4 py-2 font-medium">{model.name}</td>
                        <td className="px-4 py-2 text-gray-400">{model.provider}</td>
                        <td className="px-4 py-2">
                          <div className="flex gap-1 flex-wrap">
                            {model.capabilities?.slice(0, 3).map((cap: string, i: number) => (
                              <span key={i} className="text-xs bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded">
                                {cap}
                              </span>
                            ))}
                            {model.capabilities?.length > 3 && (
                              <span className="text-xs text-gray-500">+{model.capabilities.length - 3}</span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-2 text-gray-400">
                          {model.contextWindow ? `${model.contextWindow.toLocaleString()}` : '—'}
                        </td>
                        <td className="px-4 py-2 text-gray-400">
                          {model.costPerToken ? `$${model.costPerToken}` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Usage Statistics */}
          {usageStats.length > 0 && (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <h3 className="font-semibold mb-4">Usage Statistics</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left px-4 py-2 text-gray-400">Model</th>
                      <th className="text-left px-4 py-2 text-gray-400">Requests</th>
                      <th className="text-left px-4 py-2 text-gray-400">Tokens</th>
                      <th className="text-left px-4 py-2 text-gray-400">Cost</th>
                      <th className="text-left px-4 py-2 text-gray-400">Avg Latency</th>
                    </tr>
                  </thead>
                  <tbody>
                    {usageStats.map((stat, i) => (
                      <tr key={i} className="border-b border-gray-700 last:border-0">
                        <td className="px-4 py-2 font-medium">{stat.model}</td>
                        <td className="px-4 py-2 text-gray-400">{stat.requests?.toLocaleString() || 0}</td>
                        <td className="px-4 py-2 text-gray-400">{stat.tokens?.toLocaleString() || 0}</td>
                        <td className="px-4 py-2 text-gray-400">${stat.cost?.toFixed(4) || '0.0000'}</td>
                        <td className="px-4 py-2 text-gray-400">{stat.avgLatency?.toFixed(0) || 0}ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
