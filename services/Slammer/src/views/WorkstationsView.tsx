// Workstations view — manage coding workstations

import { useState, useEffect } from 'react';
import { api } from '../lib/api';

export default function WorkstationsView() {
  const [workers, setWorkers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getWorkers()
      .then((data) => setWorkers(data.workers || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Workstations</h2>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm">
          + New Workstation
        </button>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading workstations...</p>
      ) : error ? (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-400">
          {error}
        </div>
      ) : workers.length === 0 ? (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <span className="text-4xl">🖥️</span>
          <h3 className="text-lg font-semibold mt-4">No Workstations</h3>
          <p className="text-gray-400 mt-2 max-w-md mx-auto">
            Workstations are isolated coding environments managed by Slinker.
            Each workstation runs in a Git worktree with its own session.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {workers.map((worker) => (
            <div key={worker.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold">{worker.name || worker.id.slice(0, 8)}</h3>
                  <p className="text-sm text-gray-400 mt-1">
                    Status: <span className={worker.status === 'idle' ? 'text-green-400' : 'text-blue-400'}>
                      {worker.status}
                    </span>
                  </p>
                </div>
              </div>
              {worker.project && (
                <p className="text-sm text-gray-400 mt-3">Project: {worker.project}</p>
              )}
              <div className="mt-4 text-xs text-gray-500">
                <span>Tasks: {worker.tasksCompleted || 0}</span>
                <span className="mx-2">|</span>
                <span>Uptime: {worker.uptime || '—'}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
