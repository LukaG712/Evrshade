// Layout component with sidebar navigation

import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { checkGrafanaHealth } from '../lib/api';

const navItems = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/agents', label: 'Agents', icon: '🤖' },
  { path: '/missions', label: 'Missions', icon: '🎯' },
  { path: '/tasks', label: 'Tasks', icon: '⚡' },
  { path: '/workflows', label: 'Workflows', icon: '🔄' },
  { path: '/knowledge', label: 'Knowledge', icon: '🧠' },
  { path: '/models', label: 'Models', icon: '🔮' },
  { path: '/notifications', label: 'Notifications', icon: '🔔' },
  { path: '/logs', label: 'Logs', icon: '📋' },
  { path: '/metrics', label: 'Metrics', icon: '📈' },
  { path: '/diagnostics', label: 'Diagnostics', icon: '🔧' },
  { path: '/plugins', label: 'Plugins', icon: '🔌' },
  { path: '/terminal', label: 'Terminal', icon: '💻' },
  { path: '/workstations', label: 'Workstations', icon: '🖥️' },
  { path: '/settings', label: 'Settings', icon: '⚙️' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [grafanaHealthy, setGrafanaHealthy] = useState<boolean | null>(null);

  // Poll Grafana health on mount
  useEffect(() => {
    checkGrafanaHealth().then(setGrafanaHealthy);
    const interval = setInterval(() => checkGrafanaHealth().then(setGrafanaHealthy), 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex">
      {/* Sidebar */}
      <aside
        className={`${
          collapsed ? 'w-16' : 'w-64'
        } bg-gray-800 border-r border-gray-700 flex flex-col transition-all duration-200`}
      >
        {/* Logo */}
        <div className="p-4 border-b border-gray-700 flex items-center gap-3">
          <span className="text-2xl">👻</span>
          {!collapsed && <span className="font-bold text-lg">Evershade</span>}
        </div>

        {/* Nav */}
        <nav className="flex-1 py-4 overflow-y-auto">
          {navItems.map((item) => {
            const active = location.pathname === item.path ||
              (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                  active
                    ? 'bg-gray-700 text-white border-r-2 border-blue-500'
                    : 'text-gray-400 hover:text-white hover:bg-gray-750'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700 space-y-2">
          {/* Grafana link */}
          <a
            href="/grafana"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-white"
          >
            <span className={`w-2 h-2 rounded-full ${
              grafanaHealthy === true
                ? 'bg-green-500'
                : grafanaHealthy === false
                ? 'bg-red-500'
                : 'bg-yellow-500 animate-pulse'
            }`} />
            {!collapsed && <span>Grafana</span>}
          </a>

          {/* Toggle */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-full text-sm text-gray-400 hover:text-white"
          >
            {!collapsed ? '◀ Collapse' : '▶'}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <header className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">
            {navItems.find((i) => i.path === location.pathname)?.label || 'Dashboard'}
          </h1>
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <span>v2.0.0</span>
          </div>
        </header>
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
