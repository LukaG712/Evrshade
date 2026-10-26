// Tasks view — monitor execution tasks

import { useState, useEffect } from 'react';
import { api } from '../lib/api';

export default function TasksView() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getTasks()
      .then((data) => setTasks(data.tasks || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const statusColor = (status: string) =>
    status === 'completed' ? 'text-green-400' :
    status === 'running' ? 'text-blue-400' :
    status === 'failed' ? 'text-red-400' :
    'text-yellow-400';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Tasks</h2>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm">
          + New Task
        </button>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading tasks...</p>
      ) : error ? (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-400">
          {error}
        </div>
      ) : tasks.length === 0 ? (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <p className="text-gray-400">No tasks yet.</p>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left px-6 py-3 text-gray-400">Name</th>
                <th className="text-left px-6 py-3 text-gray-400">Status</th>
                <th className="text-left px-6 py-3 text-gray-400">Worker</th>
                <th className="text-left px-6 py-3 text-gray-400">Progress</th>
                <th className="text-left px-6 py-3 text-gray-400">Created</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id} className="border-b border-gray-700 last:border-0">
                  <td className="px-6 py-3 font-medium">{task.name || task.id.slice(0, 8)}</td>
                  <td className={`px-6 py-3 ${statusColor(task.status)}`}>{task.status}</td>
                  <td className="px-6 py-3 text-gray-400">{task.worker || '—'}</td>
                  <td className="px-6 py-3">
                    <div className="w-24 bg-gray-700 rounded-full h-1.5">
                      <div className="bg-blue-400 h-1.5 rounded-full" style={{ width: `${task.progress}%` }} />
                    </div>
                  </td>
                  <td className="px-6 py-3 text-gray-400 text-xs">
                    {new Date(task.createdAt).toLocaleString()}
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
