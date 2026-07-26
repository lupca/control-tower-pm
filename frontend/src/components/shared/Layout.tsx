import React from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  ListTodo,
  KanbanSquare,
  FolderGit2,
  Bot,
  Sun,
  Moon,
  Menu,
  X,
  Activity,
  Bell,
  Search,
  SlidersHorizontal
} from 'lucide-react';
import { useUIStore } from '../../lib/store';
import { useQuery } from '@tanstack/react-query';
import { healthApi } from '../../lib/api';

export const Layout: React.FC = () => {
  const { sidebarOpen, toggleSidebar, preferences, toggleTheme, togglePanel } = useUIStore();
  const location = useLocation();

  // Query system health for status badge
  const { data: health } = useQuery({
    queryKey: ['system-health'],
    queryFn: healthApi.getHealth,
    refetchInterval: 15000,
  });

  const isHealthy = health?.status === 'healthy';

  const navItems = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    { label: 'Tasks', path: '/tasks', icon: ListTodo },
    { label: 'Kanban', path: '/kanban', icon: KanbanSquare },
    { label: 'Projects', path: '/projects', icon: FolderGit2 },
    { label: 'Agents', path: '/agents', icon: Bot },
  ];

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-slate-900/90 backdrop-blur-lg border-r border-slate-800 transition-transform duration-300 ease-in-out md:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } flex flex-col`}
      >
        {/* Brand Header */}
        <div className="h-16 px-6 flex items-center justify-between border-b border-slate-800/80">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="font-bold tracking-tight text-white text-base">Control Tower</span>
              <span className="ml-1.5 px-1.5 py-0.5 text-[10px] font-semibold bg-indigo-500/20 text-indigo-300 rounded-full border border-indigo-500/30">
                v2.0
              </span>
            </div>
          </div>
          <button
            onClick={toggleSidebar}
            className="md:hidden text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          <div className="px-3 mb-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Overview & Management
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.path === '/'
                ? location.pathname === '/'
                : location.pathname.startsWith(item.path);

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive: active }) =>
                  `flex items-center px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group ${
                    active || isActive
                      ? 'bg-gradient-to-r from-indigo-600/90 to-blue-600/80 text-white shadow-md shadow-indigo-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon
                  className={`h-4 w-4 mr-3 transition-colors ${
                    isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
                  }`}
                />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Health / System Footer */}
        <div className="p-4 border-t border-slate-800/80">
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <span className="relative flex h-2.5 w-2.5">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full ${
                    isHealthy ? 'bg-emerald-400' : 'bg-amber-400'
                  } opacity-75`}
                />
                <span
                  className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                    isHealthy ? 'bg-emerald-500' : 'bg-amber-500'
                  }`}
                />
              </span>
              <span className="text-xs font-medium text-slate-300">
                {isHealthy ? 'Backend Ready' : 'Connecting...'}
              </span>
            </div>
            <Activity className="h-4 w-4 text-slate-500" />
          </div>
        </div>
      </aside>

      {/* Main Container */}
      <div className={`flex-1 flex flex-col min-w-0 transition-all duration-300 md:ml-64`}>
        {/* Header */}
        <header className="h-16 sticky top-0 z-30 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 px-6 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleSidebar}
              className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 md:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>

            {/* Quick Search */}
            <div className="relative hidden sm:block w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search tasks, projects, agents..."
                className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-900/90 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/60 transition-all"
              />
            </div>
          </div>

          {/* Action Icons & Theme Toggle */}
          <div className="flex items-center space-x-3">
            <button
              onClick={() => togglePanel('preferences')}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-all"
              title="Preferences"
            >
              <SlidersHorizontal className="h-4.5 w-4.5" />
            </button>

            <button
              onClick={() => togglePanel('notifications')}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-all relative"
              title="Notifications"
            >
              <Bell className="h-4.5 w-4.5" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-indigo-500"></span>
            </button>

            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-all"
              title="Toggle Theme"
            >
              {preferences.theme === 'dark' ? (
                <Sun className="h-4.5 w-4.5 text-amber-400" />
              ) : (
                <Moon className="h-4.5 w-4.5 text-indigo-400" />
              )}
            </button>

            <div className="h-6 w-px bg-slate-800 mx-1"></div>

            <div className="flex items-center space-x-2.5 pl-1">
              <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-indigo-400">
                AI
              </div>
              <div className="hidden lg:block text-left">
                <div className="text-xs font-semibold text-slate-200">Operator</div>
                <div className="text-[10px] text-slate-400">Antigravity Agent</div>
              </div>
            </div>
          </div>
        </header>

        {/* Content Outlet */}
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
