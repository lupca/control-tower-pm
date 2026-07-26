import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { tasksApi, agentsApi, projectsApi } from '../lib/api';
import { NavLink } from 'react-router-dom';
import {
  ListTodo,
  CheckCircle2,
  Clock,
  AlertCircle,
  Bot,
  FolderGit2,
  ArrowUpRight,
  Sparkles,
  ChevronRight
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { data: tasks = [] } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.getTasks(),
  });

  const { data: agents = [] } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsApi.getAgents(),
  });

  const { data: projects = [] } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.getProjects(),
  });

  const completedCount = tasks.filter((t) => t.status === 'done').length;
  const inProgressCount = tasks.filter((t) => t.status === 'in_progress').length;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-900/60 via-slate-900/90 to-slate-950 p-6 md:p-8 border border-indigo-500/20 shadow-2xl">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Control Tower V2 Dashboard</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
            Autonomous Agent Orchestration
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed">
            Monitor background agent execution, manage software development task queues, track project status, and view real-time logs.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <NavLink
              to="/kanban"
              className="inline-flex items-center px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all"
            >
              Open Kanban Board
              <ChevronRight className="h-4 w-4 ml-1" />
            </NavLink>
            <NavLink
              to="/tasks"
              className="inline-flex items-center px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all"
            >
              View Task List
            </NavLink>
          </div>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-panel p-5 rounded-2xl glass-panel-hover flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400">Total Tasks</p>
            <h3 className="text-2xl font-bold text-white mt-1">{tasks.length}</h3>
            <span className="text-[11px] text-slate-400 mt-1 inline-block">All project queues</span>
          </div>
          <div className="h-12 w-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <ListTodo className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl glass-panel-hover flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400">In Progress</p>
            <h3 className="text-2xl font-bold text-amber-400 mt-1">{inProgressCount}</h3>
            <span className="text-[11px] text-amber-400/80 mt-1 inline-block">Active agents running</span>
          </div>
          <div className="h-12 w-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Clock className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl glass-panel-hover flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400">Completed</p>
            <h3 className="text-2xl font-bold text-emerald-400 mt-1">{completedCount}</h3>
            <span className="text-[11px] text-emerald-400/80 mt-1 inline-block">Verified tasks</span>
          </div>
          <div className="h-12 w-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl glass-panel-hover flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400">Active Agents</p>
            <h3 className="text-2xl font-bold text-indigo-400 mt-1">{agents.length}</h3>
            <span className="text-[11px] text-indigo-400/80 mt-1 inline-block">Autonomous workers</span>
          </div>
          <div className="h-12 w-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Bot className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Main Content Layout - 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Recent Tasks */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center">
              <ListTodo className="h-5 w-5 mr-2 text-indigo-400" />
              Recent Tasks
            </h2>
            <NavLink to="/tasks" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center">
              View All <ArrowUpRight className="h-3.5 w-3.5 ml-1" />
            </NavLink>
          </div>

          <div className="glass-panel rounded-2xl overflow-hidden">
            {tasks.length === 0 ? (
              <div className="p-8 text-center space-y-3">
                <AlertCircle className="h-8 w-8 text-slate-500 mx-auto" />
                <p className="text-slate-400 text-sm">No tasks found in the database yet.</p>
                <p className="text-slate-500 text-xs">Create tasks to begin agent orchestration.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-800/80">
                {tasks.slice(0, 5).map((task) => (
                  <div key={task.id} className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-mono font-bold text-slate-400">{task.id}</span>
                        <NavLink to={`/task/${task.id}`} className="text-sm font-semibold text-slate-100 hover:text-indigo-400 transition-colors">
                          {task.title}
                        </NavLink>
                      </div>
                      <div className="flex items-center space-x-2 text-[11px] text-slate-400">
                        {task.priority && (
                          <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
                            {task.priority}
                          </span>
                        )}
                        {task.executor && <span>Executor: {task.executor}</span>}
                      </div>
                    </div>

                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${
                        task.status === 'done'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : task.status === 'in_progress'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'
                          : 'bg-slate-800 text-slate-300 border border-slate-700'
                      }`}
                    >
                      {task.status.replace('_', ' ')}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Active Agents & Projects Overview */}
        <div className="space-y-6">
          {/* Active Agents */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-white flex items-center">
                <Bot className="h-5 w-5 mr-2 text-indigo-400" />
                Agents Status
              </h2>
              <NavLink to="/agents" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300">
                View Agents
              </NavLink>
            </div>

            <div className="glass-panel p-4 rounded-2xl space-y-3">
              {agents.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-400">
                  No agents registered yet.
                </div>
              ) : (
                agents.map((agent) => (
                  <div key={agent.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-slate-200">{agent.name}</h4>
                      <p className="text-[11px] text-slate-400">{agent.role}</p>
                    </div>
                    <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400"></span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Active Projects */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-white flex items-center">
                <FolderGit2 className="h-5 w-5 mr-2 text-indigo-400" />
                Projects
              </h2>
              <NavLink to="/projects" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300">
                All Projects
              </NavLink>
            </div>

            <div className="glass-panel p-4 rounded-2xl space-y-3">
              {projects.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-400">
                  Control Tower V2 System Project
                </div>
              ) : (
                projects.map((proj) => (
                  <div key={proj.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                    <h4 className="text-xs font-bold text-slate-200">{proj.name}</h4>
                    <p className="text-[11px] text-slate-400 mt-0.5">{proj.description || 'No description provided'}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
