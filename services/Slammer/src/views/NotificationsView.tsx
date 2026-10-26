// Notifications view — notification rules and channels management

import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';

export default function NotificationsView() {
  const [rules, setRules] = useState<any[]>([]);
  const [channels, setChannels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newRule, setNewRule] = useState({ name: '', event: '', channel: '', condition: '' });

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [rulesData, channelsData] = await Promise.allSettled([
        api.getNotificationRules(),
        api.getChannels(),
      ]);

      if (rulesData.status === 'fulfilled') {
        setRules(rulesData.value.rules || []);
      }
      if (channelsData.status === 'fulfilled') {
        setChannels(channelsData.value.channels || []);
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

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createNotificationRule({
        name: newRule.name,
        event: newRule.event,
        channel: newRule.channel,
        condition: newRule.condition || undefined,
        enabled: true,
      });
      setNewRule({ name: '', event: '', channel: '', condition: '' });
      setShowCreate(false);
      fetchData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleToggle = async (id: string, currentEnabled: boolean) => {
    try {
      await api.updateNotificationRule(id, { enabled: !currentEnabled });
      fetchData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this notification rule?')) return;
    try {
      await api.deleteNotificationRule(id);
      fetchData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const eventIcon = (event: string) => {
    if (event.includes('task')) return '⚡';
    if (event.includes('mission')) return '🎯';
    if (event.includes('agent')) return '🤖';
    if (event.includes('workflow')) return '🔄';
    if (event.includes('alert')) return '🚨';
    return '📧';
  };

  const channelIcon = (channel: string) => {
    if (channel.includes('slack')) return '💬';
    if (channel.includes('discord')) return '🎮';
    if (channel.includes('email')) return '📧';
    if (channel.includes('telegram')) return '✈️';
    return '📢';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Notifications</h2>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm"
        >
          {showCreate ? 'Cancel' : '+ New Rule'}
        </button>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-4 text-red-300">✕</button>
        </div>
      )}

      {/* Create rule form */}
      {showCreate && (
        <form onSubmit={handleCreate} className="bg-gray-800 rounded-lg border border-gray-700 p-6 space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Name</label>
            <input
              type="text"
              required
              value={newRule.name}
              onChange={e => setNewRule({ ...newRule, name: e.target.value })}
              className="w-full bg-gray-900 border border-gray-600 rounded-md px-3 py-2 text-sm focus:border-blue-500 outline-none"
              placeholder="Task completion alert"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Event</label>
              <select
                required
                value={newRule.event}
                onChange={e => setNewRule({ ...newRule, event: e.target.value })}
                className="w-full bg-gray-900 border border-gray-600 rounded-md px-3 py-2 text-sm focus:border-blue-500 outline-none"
              >
                <option value="">Select event</option>
                <option value="task.completed">Task Completed</option>
                <option value="task.failed">Task Failed</option>
                <option value="mission.completed">Mission Completed</option>
                <option value="mission.failed">Mission Failed</option>
                <option value="workflow.completed">Workflow Completed</option>
                <option value="alert.triggered">Alert Triggered</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Channel</label>
              <select
                required
                value={newRule.channel}
                onChange={e => setNewRule({ ...newRule, channel: e.target.value })}
                className="w-full bg-gray-900 border border-gray-600 rounded-md px-3 py-2 text-sm focus:border-blue-500 outline-none"
              >
                <option value="">Select channel</option>
                {channels.map((ch: any) => (
                  <option key={ch.id} value={ch.id}>{ch.name}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Condition (optional)</label>
            <input
              type="text"
              value={newRule.condition}
              onChange={e => setNewRule({ ...newRule, condition: e.target.value })}
              className="w-full bg-gray-900 border border-gray-600 rounded-md px-3 py-2 text-sm focus:border-blue-500 outline-none"
              placeholder="e.g., status == 'failed'"
            />
          </div>
          <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm">
            Create Rule
          </button>
        </form>
      )}

      {/* Channels */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="font-semibold mb-4">Channels ({channels.length})</h3>
        {channels.length === 0 ? (
          <p className="text-gray-400 text-sm">No channels configured. Add channels through the Poltergeist API.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {channels.map((channel: any) => (
              <div key={channel.id} className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg border border-gray-700">
                <span className="text-2xl">{channelIcon(channel.type)}</span>
                <div className="flex-1">
                  <div className="font-medium text-sm">{channel.name}</div>
                  <div className="text-xs text-gray-500 capitalize">{channel.type}</div>
                </div>
                {channel.enabled ? (
                  <span className="text-xs text-green-400">● Active</span>
                ) : (
                  <span className="text-xs text-gray-500">○ Inactive</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Rules */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="font-semibold mb-4">Notification Rules ({rules.length})</h3>
        {loading ? (
          <p className="text-gray-400 text-sm">Loading rules...</p>
        ) : rules.length === 0 ? (
          <div className="text-center py-8">
            <span className="text-3xl">🔔</span>
            <p className="text-gray-400 mt-3">No notification rules yet. Create rules to receive alerts for events.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {rules.map((rule) => (
              <div key={rule.id} className="flex items-center justify-between p-3 bg-gray-900 rounded-lg border border-gray-700">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{eventIcon(rule.event)}</span>
                  <div>
                    <div className="font-medium text-sm flex items-center gap-2">
                      {rule.name}
                      {rule.enabled ? (
                        <span className="text-xs text-green-400">●</span>
                      ) : (
                        <span className="text-xs text-gray-500">○</span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500">
                      {rule.event} → {channelIcon(rule.channel)} {rule.channel}
                      {rule.condition && ` (if ${rule.condition})`}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleToggle(rule.id, rule.enabled)}
                    className={`text-xs px-2 py-1 rounded ${rule.enabled ? 'bg-green-900/50 text-green-400' : 'bg-gray-700 text-gray-400'}`}
                  >
                    {rule.enabled ? 'On' : 'Off'}
                  </button>
                  <button
                    onClick={() => handleDelete(rule.id)}
                    className="text-xs text-red-400 hover:text-red-300 px-2 py-1"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
