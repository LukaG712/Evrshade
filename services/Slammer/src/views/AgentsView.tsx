// Agents view — list and manage agents

import { useState, useEffect } from 'react';
import { api } from '../lib/api';

export default function AgentsView() {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getAgents()
      .then((data) => setAgents(data.agents || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const statusColor = (status: string) =>
    status === 'active' ? 'text-green-400' :
    status === 'idle' ? 'text-blue-400' :
    status === 'error' ? 'text-red-400' :
    'text-gray-400';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Agents</h2>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm">
          + New Agent
        </button>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading agents...</p>
      ) : error ? (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-400">
          {error}
        </div>
      ) : agents.length === 0 ? (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <p className="text-gray-400">No agents configured yet.</p>
          <p className="text-sm text-gray-500 mt-2">Create an agent to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <div key={agent.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-gray-600 transition-colors">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold">{agent.name}</h3>
                  <p className="text-sm text-gray-400 mt-1">{agent.description || 'No description'}</p>
                </div>
                <span className={`text-sm ${statusColor(agent.status)}`}>{agent.status}</span>
              </div>
              {agent.model && (
                <p className="text-xs text-gray-500 mt-3">Model: {agent.model}</p>
              )}
              <div className="flex items-center justify-between mt-4 text-xs text-gray-500">
                <span>Created: {new Date(agent.createdAt).toLocaleDateString()}</span>
                <div className="flex gap-2">
                  <button className="text-blue-400 hover:text-blue-300">Edit</button>
                  <button className="text-red-400 hover:text-red-300">Delete</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
