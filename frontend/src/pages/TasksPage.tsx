import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { tasksApi, Task } from '../lib/api';
import { NavLink } from 'react-router-dom';
import {
  ListTodo,
  Search,
  Filter,
  Plus,
  Clock,
  AlertCircle,
  ChevronRight,
  User,
  Tag
} from 'lucide-react';

export const TasksPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.getTasks(),
  });

  const filteredTasks = tasks.filter((task: Task) => {
    const matchesSearch =
      task.title.toLowerCase().includes(search.toLowerCase()) ||
      task.id.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'all' || task.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || task.priority === priorityFilter;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center">
            <ListTodo className="h-6 w-6 mr-2 text-indigo-400" />
            Task Management
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            View, search, and manage software development tasks for agent execution.
          </p>
        </div>

        <button className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all self-start sm:self-auto">
          <Plus className="h-4 w-4 mr-1.5" />
          Create Task
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="glass-panel p-4 rounded-2xl flex flex-col md:flex-row gap-4 items-center justify-between">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ID or title..."
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-950/80 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/60"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <Filter className="h-3.5 w-3.5" />
            <span>Filters:</span>
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 text-xs bg-slate-950/80 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="all">All Statuses</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="review">Review</option>
            <option value="done">Done</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-1.5 text-xs bg-slate-950/80 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="all">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Task List */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            Loading tasks...
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <AlertCircle className="h-8 w-8 text-slate-500 mx-auto" />
            <p className="text-slate-300 text-sm font-semibold">No tasks found</p>
            <p className="text-slate-500 text-xs">Try adjusting your search or filters.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {filteredTasks.map((task) => (
              <NavLink
                key={task.id}
                to={`/task/${task.id}`}
                className="p-4 md:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-800/40 transition-colors group block"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center space-x-3">
                    <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                      {task.id}
                    </span>
                    <h3 className="text-sm font-semibold text-slate-100 group-hover:text-indigo-300 transition-colors">
                      {task.title}
                    </h3>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 pt-1">
                    {task.priority && (
                      <span className="flex items-center space-x-1 text-[11px] text-slate-300 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                        <Tag className="h-3 w-3 text-slate-500" />
                        <span className="capitalize">{task.priority} Priority</span>
                      </span>
                    )}

                    {task.executor && (
                      <span className="flex items-center space-x-1 text-[11px] text-slate-400">
                        <User className="h-3 w-3 text-slate-500" />
                        <span>Executor: {task.executor}</span>
                      </span>
                    )}

                    {task.deadline && (
                      <span className="flex items-center space-x-1 text-[11px] text-slate-400">
                        <Clock className="h-3 w-3 text-slate-500" />
                        <span>Due: {task.deadline}</span>
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between md:justify-end space-x-4">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${
                      task.status === 'done'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : task.status === 'in_progress'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'
                        : 'bg-slate-800 text-slate-300 border border-slate-700'
                    }`}
                  >
                    {task.status.replace('_', ' ')}
                  </span>
                  <ChevronRight className="h-4 w-4 text-slate-600 group-hover:text-indigo-400 transition-colors" />
                </div>
              </NavLink>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
