// Missions view — track mission lifecycle

import { useState, useEffect } from 'react';
import { api } from '../lib/api';

export default function MissionsView() {
  const [missions, setMissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getMissions()
      .then((data) => setMissions(data.missions || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const statusColor = (status: string) =>
    status === 'completed' ? 'text-green-400' :
    status === 'executing' ? 'text-blue-400' :
    status === 'planning' ? 'text-yellow-400' :
    status === 'failed' ? 'text-red-400' :
    status === 'paused' ? 'text-orange-400' :
    'text-gray-400';

  const progressColor = (status: string) =>
    status === 'completed' ? 'bg-green-400' :
    status === 'failed' ? 'bg-red-400' :
    'bg-blue-400';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Missions</h2>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm">
          + New Mission
        </button>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading missions...</p>
      ) : error ? (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-400">
          {error}
        </div>
      ) : missions.length === 0 ? (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <p className="text-gray-400">No missions yet.</p>
          <p className="text-sm text-gray-500 mt-2">Create a mission to start an AI workflow.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {missions.map((mission) => (
            <div key={mission.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold">{mission.name}</h3>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(mission.createdAt).toLocaleString()}
                  </p>
                </div>
                <span className={`text-sm font-medium ${statusColor(mission.status)}`}>
                  {mission.status}
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-gray-700 rounded-full h-2 mb-3">
                <div
                  className={`h-2 rounded-full transition-all ${progressColor(mission.status)}`}
                  style={{ width: `${mission.progress}%` }}
                />
              </div>

              {/* Milestones */}
              {mission.milestones && mission.milestones.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {mission.milestones.map((ms: any) => (
                    <span
                      key={ms.id}
                      className={`text-xs px-2 py-1 rounded ${
                        ms.status === 'completed'
                          ? 'bg-green-900/50 text-green-400'
                          : ms.status === 'in_progress'
                          ? 'bg-blue-900/50 text-blue-400'
                          : ms.status === 'failed'
                          ? 'bg-red-900/50 text-red-400'
                          : 'bg-gray-700 text-gray-400'
                      }`}
                    >
                      {ms.name}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between mt-4 text-xs text-gray-500">
                <span>ID: {mission.id.slice(0, 8)}...</span>
                <div className="flex gap-2">
                  <button className="text-blue-400 hover:text-blue-300">Details</button>
                  {mission.status === 'executing' && (
                    <button className="text-orange-400 hover:text-orange-300">Pause</button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
