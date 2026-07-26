import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Layout } from './components/shared/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { TasksPage } from './pages/TasksPage';
import { KanbanPage } from './pages/KanbanPage';
import { TaskDetailPage } from './pages/TaskDetailPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { AgentsPage } from './pages/AgentsPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: 'tasks',
        element: <TasksPage />,
      },
      {
        path: 'kanban',
        element: <KanbanPage />,
      },
      {
        path: 'task/:id',
        element: <TaskDetailPage />,
      },
      {
        path: 'projects',
        element: <ProjectsPage />,
      },
      {
        path: 'agents',
        element: <AgentsPage />,
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);
