// Workflows view — workflow management with real API integration

import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';

export default function WorkflowsView() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newWorkflow, setNewWorkflow] = useState({ name: '', description: '', steps: '[]' });
  const [selectedWorkflow, setSelectedWorkflow] = useState<any | null>(null);
  const [runs, setRuns] = useState<any[]>([]);

  const fetchWorkflows = useCallback(async () => {
    try {
      const data = await api.getWorkflows();
      setWorkflows(data.workflows || []);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const steps = JSON.parse(newWorkflow.steps);
      await api.createWorkflow({
        name: newWorkflow.name,
        description: newWorkflow.description,
        steps,
        triggers: [{ type: 'manual' }],
      });
      setNewWorkflow({ name: '', description: '', steps: '[]' });
      setShowCreate(false);
      fetchWorkflows();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleExecute = async (id: string) => {
    try {
      await api.executeWorkflow(id);
      fetchWorkflows();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleToggleStatus = async (id: string, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'active' ? 'disabled' : 'active';
      await api.updateWorkflow(id, { status: newStatus });
      fetchWorkflows();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this workflow?')) return;
    try {
      await api.deleteWorkflow(id);
      fetchWorkflows();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const viewRuns = async (id: string, name: string) => {
    try {
      const data = await api.getWorkflowRuns(id);
      setRuns(data.runs || []);
      setSelectedWorkflow({ id, name });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const statusColor = (status: string) =>
    status === 'active' ? 'text-green-400' :
    status === 'paused' ? 'text-yellow-400' :
    status === 'disabled' ? 'text-gray-500' :
    'text-blue-400';

  const runStatusColor = (status: string) =>
    status === 'completed' ? 'text-green-400' :
    status === 'running' ? 'text-blue-400' :
    status === 'failed' ? 'text-red-400' :
    status === 'cancelled' ? 'text-gray-500' :
    'text-yellow-400';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Workflows</h2>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm"
        >
          {showCreate ? 'Cancel' : '+ New Workflow'}
        </button>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-4 text-red-300">✕</button>
        </div>
      )}

      {/* Create form */}
      {showCreate && (
        <form onSubmit={handleCreate} className="bg-gray-800 rounded-lg border border-gray-700 p-6 space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Name</label>
            <input
              type="text"
              required
              value={newWorkflow.name}
              onChange={e => setNewWorkflow({ ...newWorkflow, name: e.target.value })}
              className="w-full bg-gray-900 border border-gray-600 rounded-md px-3 py-2 text-sm focus:border-blue-500 outline-none"
              placeholder="My Workflow"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Description</label>
            <input
              type="text"
              value={newWorkflow.description}
              onChange={e => setNewWorkflow({ ...newWorkflow, description: e.target.value })}
              className="w-full bg-gray-900 border border-gray-600 rounded-md px-3 py-2 text-sm focus:border-blue-500 outline-none"
              placeholder="What this workflow does"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Steps (JSON array)</label>
            <textarea
              value={newWorkflow.steps}
              onChange={e => setNewWorkflow({ ...newWorkflow, steps: e.target.value })}
              className="w-full bg-gray-900 border border-gray-600 rounded-md px-3 py-2 text-sm focus:border-blue-500 outline-none font-mono"
              rows={4}
              placeholder='[{"step_id": "step1", "name": "Step 1", "type": "http_request", "config": {"url": "https://example.com"}}]'
            />
          </div>
          <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm">
            Create Workflow
          </button>
        </form>
      )}

      {/* Workflow runs modal */}
      {selectedWorkflow && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Runs for: {selectedWorkflow.name}</h3>
            <button onClick={() => setSelectedWorkflow(null)} className="text-gray-400 hover:text-white">✕</button>
          </div>
          {runs.length === 0 ? (
            <p className="text-gray-400 text-sm">No runs yet.</p>
          ) : (
            <div className="space-y-2">
              {runs.map((run) => (
                <div key={run.id} className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0">
                  <div className="flex items-center gap-3">
                    <span className={`text-sm ${runStatusColor(run.status)}`}>{run.status}</span>
                    <span className="text-xs text-gray-500">{run.triggerType}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {run.startedAt ? new Date(run.startedAt).toLocaleString() : '—'}
                    {run.error && <span className="text-red-400 ml-2">{run.error}</span>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Workflows list */}
      {loading ? (
        <p className="text-gray-400">Loading workflows...</p>
      ) : workflows.length === 0 ? (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <span className="text-4xl">🔄</span>
          <h3 className="text-lg font-semibold mt-4">No Workflows Yet</h3>
          <p className="text-gray-400 mt-2 max-w-md mx-auto">
            Create automated workflows that chain together agents, tasks, and external services.
            Define triggers, steps, and conditions to orchestrate complex AI operations.
          </p>
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
              <h4 className="font-medium">📥 Triggers</h4>
              <p className="text-sm text-gray-400 mt-1">Webhooks, schedules, events</p>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
              <h4 className="font-medium">⚡ Actions</h4>
              <p className="text-sm text-gray-400 mt-1">Agents, tasks, API calls</p>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
              <h4 className="font-medium">🔀 Conditions</h4>
              <p className="text-sm text-gray-400 mt-1">Branching, loops, retries</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left px-6 py-3 text-gray-400">Name</th>
                <th className="text-left px-6 py-3 text-gray-400">Status</th>
                <th className="text-left px-6 py-3 text-gray-400">Runs</th>
                <th className="text-left px-6 py-3 text-gray-400">Last Run</th>
                <th className="text-right px-6 py-3 text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {workflows.map((wf) => (
                <tr key={wf.id} className="border-b border-gray-700 last:border-0">
                  <td className="px-6 py-3">
                    <div>
                      <div className="font-medium">{wf.name}</div>
                      {wf.description && <div className="text-xs text-gray-500">{wf.description}</div>}
                    </div>
                  </td>
                  <td className={`px-6 py-3 ${statusColor(wf.status)}`}>{wf.status}</td>
                  <td className="px-6 py-3 text-gray-400">{wf.runs || 0}</td>
                  <td className="px-6 py-3 text-gray-400 text-xs">
                    {wf.lastRun ? new Date(wf.lastRun).toLocaleString() : '—'}
                  </td>
                  <td className="px-6 py-3 text-right space-x-2">
                    <button
                      onClick={() => viewRuns(wf.id, wf.name)}
                      className="text-blue-400 hover:text-blue-300 text-xs"
                    >
                      Runs
                    </button>
                    {wf.status === 'active' && (
                      <button
                        onClick={() => handleExecute(wf.id)}
                        className="text-green-400 hover:text-green-300 text-xs"
                      >
                        Run
                      </button>
                    )}
                    <button
                      onClick={() => handleToggleStatus(wf.id, wf.status)}
                      className="text-yellow-400 hover:text-yellow-300 text-xs"
                    >
                      {wf.status === 'active' ? 'Disable' : 'Enable'}
                    </button>
                    <button
                      onClick={() => handleDelete(wf.id)}
                      className="text-red-400 hover:text-red-300 text-xs"
                    >
                      Delete
                    </button>
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
