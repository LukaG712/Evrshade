// Logs view — view structured logs from Sneaker

import { useState, useEffect } from 'react';
import { api } from '../lib/api';

const levelColors: Record<string, string> = {
  debug: 'text-gray-400',
  info: 'text-blue-400',
  warn: 'text-yellow-400',
  error: 'text-red-400',
  critical: 'text-red-300 font-bold',
};

export default function LogsView() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterService, setFilterService] = useState('');
  const [filterLevel, setFilterLevel] = useState('');

  const fetchLogs = () => {
    setLoading(true);
    api.getLogs({ service: filterService || undefined, level: filterLevel || undefined, limit: 200 })
      .then((data) => setLogs(data.logs || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLogs();
  }, [filterService, filterLevel]);

  return (
    <div className="space-y-6">
      {/* Filters */}
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

        <select
          value={filterLevel}
          onChange={(e) => setFilterLevel(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm"
        >
          <option value="">All Levels</option>
          <option value="debug">Debug</option>
          <option value="info">Info</option>
          <option value="warn">Warn</option>
          <option value="error">Error</option>
          <option value="critical">Critical</option>
        </select>

        <button
          onClick={fetchLogs}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading logs...</p>
      ) : error ? (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-400">
          {error}
        </div>
      ) : logs.length === 0 ? (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <p className="text-gray-400">No logs found.</p>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="max-h-[600px] overflow-y-auto font-mono text-sm">
            {logs.map((log) => (
              <div key={log.id} className="border-b border-gray-700/50 px-4 py-2 hover:bg-gray-750">
                <div className="flex items-start gap-3">
                  <span className="text-gray-500 whitespace-nowrap text-xs">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className={`uppercase text-xs font-bold w-16 ${levelColors[log.level] || 'text-gray-400'}`}>
                    {log.level}
                  </span>
                  <span className="text-cyan-400 text-xs w-24 truncate">{log.service}</span>
                  <span className="text-gray-300 break-all">{log.message}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
