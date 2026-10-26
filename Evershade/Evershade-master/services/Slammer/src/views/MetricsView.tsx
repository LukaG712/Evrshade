// Metrics view — view metrics from Sneaker

import { useState, useEffect } from 'react';
import { api } from '../lib/api';

export default function MetricsView() {
  const [metrics, setMetrics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterService, setFilterService] = useState('');

  const fetchMetrics = () => {
    setLoading(true);
    api.getMetrics({ service: filterService || undefined, limit: 100 })
      .then((data) => setMetrics(data.metrics || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMetrics();
  }, [filterService]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <select
          value={filterService}
          onChange={(e) => setFilterService(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm"
        >
          <option value="">All Services</option>
          <option value="Greenie">Greenie</option>
          <option value="Slinker">Slinker</option>
          <option value="Trapper">Trapper</option>
          <option value="Gobber">Gobber</option>
          <option value="Sneaker">Sneaker</option>
          <option value="Hider">Hider</option>
          <option value="Poltergeist">Poltergeist</option>
          <option value="Shrewd">Shrewd</option>
        </select>

        <button
          onClick={fetchMetrics}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm"
        >
          Refresh
        </button>

        <a
          href="/prometheus"
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm ml-auto"
        >
          Open Prometheus
        </a>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading metrics...</p>
      ) : error ? (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-400">
          {error}
        </div>
      ) : metrics.length === 0 ? (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <p className="text-gray-400">No metrics found.</p>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left px-6 py-3 text-gray-400">Name</th>
                <th className="text-left px-6 py-3 text-gray-400">Service</th>
                <th className="text-left px-6 py-3 text-gray-400">Type</th>
                <th className="text-right px-6 py-3 text-gray-400">Value</th>
                <th className="text-left px-6 py-3 text-gray-400">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((m, i) => (
                <tr key={i} className="border-b border-gray-700 last:border-0">
                  <td className="px-6 py-3 font-medium">{m.name}</td>
                  <td className="px-6 py-3 text-cyan-400">{m.service_name}</td>
                  <td className="px-6 py-3 text-gray-400">
                    <span className="px-2 py-0.5 bg-gray-700 rounded text-xs">{m.metric_type}</span>
                  </td>
                  <td className="px-6 py-3 text-right font-mono">{m.value}</td>
                  <td className="px-6 py-3 text-gray-400 text-xs">
                    {new Date(m.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
