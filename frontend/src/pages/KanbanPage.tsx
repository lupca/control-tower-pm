import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { tasksApi, Task } from '../lib/api';
import { NavLink } from 'react-router-dom';
import {
  KanbanSquare,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
  Tag,
  User
} from 'lucide-react';

interface Column {
  id: Task['status'];
  title: string;
  color: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const KanbanPage: React.FC = () => {
  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.getTasks(),
  });

  const columns: Column[] = [
    { id: 'todo', title: 'To Do', color: 'border-slate-700 bg-slate-900/40 text-slate-300', icon: Clock },
    { id: 'in_progress', title: 'In Progress', color: 'border-amber-500/40 bg-amber-500/5 text-amber-400', icon: AlertCircle },
    { id: 'review', title: 'Review', color: 'border-indigo-500/40 bg-indigo-500/5 text-indigo-400', icon: KanbanSquare },
    { id: 'done', title: 'Done', color: 'border-emerald-500/40 bg-emerald-500/5 text-emerald-400', icon: CheckCircle2 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center">
            <KanbanSquare className="h-6 w-6 mr-2 text-indigo-400" />
            Kanban Board
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Visual task tracking across execution stages.
          </p>
        </div>

        <button className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all self-start sm:self-auto">
          <Plus className="h-4 w-4 mr-1.5" />
          Add Task
        </button>
      </div>

      {/* Kanban Board Columns */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-xs">
          Loading board...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {columns.map((col) => {
            const ColumnIcon = col.icon;
            const columnTasks = tasks.filter((t) => t.status === col.id);

            return (
              <div key={col.id} className="flex flex-col h-full min-h-[500px] glass-panel rounded-2xl p-4">
                {/* Column Header */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-3">
                  <div className="flex items-center space-x-2">
                    <ColumnIcon className={`h-4 w-4 ${col.color.split(' ')[2]}`} />
                    <h3 className="text-sm font-bold text-slate-200">{col.title}</h3>
                  </div>
                  <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded-full bg-slate-950 border border-slate-800 text-slate-400">
                    {columnTasks.length}
                  </span>
                </div>

                {/* Cards Container */}
                <div className="flex-1 space-y-3 overflow-y-auto pr-1">
                  {columnTasks.length === 0 ? (
                    <div className="h-32 border border-dashed border-slate-800/80 rounded-xl flex items-center justify-center text-xs text-slate-500">
                      No tasks in {col.title}
                    </div>
                  ) : (
                    columnTasks.map((task) => (
                      <NavLink
                        key={task.id}
                        to={`/task/${task.id}`}
                        className="block p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 hover:border-slate-700 transition-all hover:shadow-lg hover:shadow-indigo-500/5 group"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[11px] font-mono font-bold text-indigo-400">
                            {task.id}
                          </span>
                          {task.priority && (
                            <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                              {task.priority}
                            </span>
                          )}
                        </div>

                        <h4 className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors line-clamp-2 mb-3">
                          {task.title}
                        </h4>

                        <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-900">
                          <div className="flex items-center space-x-1">
                            <User className="h-3 w-3 text-slate-500" />
                            <span>{task.executor || 'Unassigned'}</span>
                          </div>
                          {task.files && task.files.length > 0 && (
                            <div className="flex items-center space-x-1 text-slate-500">
                              <Tag className="h-3 w-3" />
                              <span>{task.files.length} files</span>
                            </div>
                          )}
                        </div>
                      </NavLink>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
