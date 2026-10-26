import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardView from './views/DashboardView';
import AgentsView from './views/AgentsView';
import MissionsView from './views/MissionsView';
import TasksView from './views/TasksView';
import LogsView from './views/LogsView';
import MetricsView from './views/MetricsView';
import PluginsView from './views/PluginsView';
import TerminalView from './views/TerminalView';
import WorkflowsView from './views/WorkflowsView';
import WorkstationsView from './views/WorkstationsView';
import SettingsView from './views/SettingsView';
import KnowledgeView from './views/KnowledgeView';
import ModelsView from './views/ModelsView';
import NotificationsView from './views/NotificationsView';
import DiagnosticsView from './views/DiagnosticsView';

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardView />} />
          <Route path="/agents" element={<AgentsView />} />
          <Route path="/missions" element={<MissionsView />} />
          <Route path="/tasks" element={<TasksView />} />
          <Route path="/workflows" element={<WorkflowsView />} />
          <Route path="/knowledge" element={<KnowledgeView />} />
          <Route path="/models" element={<ModelsView />} />
          <Route path="/notifications" element={<NotificationsView />} />
          <Route path="/logs" element={<LogsView />} />
          <Route path="/metrics" element={<MetricsView />} />
          <Route path="/diagnostics" element={<DiagnosticsView />} />
          <Route path="/plugins" element={<PluginsView />} />
          <Route path="/terminal" element={<TerminalView />} />
          <Route path="/workstations" element={<WorkstationsView />} />
          <Route path="/settings" element={<SettingsView />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
