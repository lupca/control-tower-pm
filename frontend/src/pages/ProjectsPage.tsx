import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '../lib/api';
import { FolderGit2, Plus, ArrowUpRight, FolderCheck, Layers } from 'lucide-react';

export const ProjectsPage: React.FC = () => {
  const { data: projects = [], isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.getProjects(),
  });

  const defaultProjects = [
    {
      id: 'control-tower-v2',
      name: 'Control Tower V2',
      description: 'Autonomous AI Agent Orchestration & Task Execution Engine',
      status: 'active',
      tasks_count: 20,
      completed_count: 15,
      created_at: '2026-07-26',
    },
    {
      id: 'rag-engine',
      name: 'RAG Knowledge Core',
      description: 'Vector store indexing & document retrieval pipelines',
      status: 'active',
      tasks_count: 8,
      completed_count: 8,
      created_at: '2026-07-20',
    },
  ];

  const projectList = projects.length > 0 ? projects : defaultProjects;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center">
            <FolderGit2 className="h-6 w-6 mr-2 text-indigo-400" />
            Projects Workspace
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Organize tasks, agents, and system resources by project modules.
          </p>
        </div>

        <button className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all self-start sm:self-auto">
          <Plus className="h-4 w-4 mr-1.5" />
          New Project
        </button>
      </div>

      {/* Grid of Projects */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading projects...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {projectList.map((project) => (
            <div
              key={project.id}
              className="glass-panel p-6 rounded-2xl glass-panel-hover flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2.5 py-0.5 rounded border border-indigo-500/20">
                    {project.id}
                  </span>
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 capitalize">
                    {project.status}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white mt-1">{project.name}</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {project.description || 'No detailed description provided.'}
                </p>
              </div>

              <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                <div className="flex items-center space-x-4">
                  <span className="flex items-center">
                    <Layers className="h-3.5 w-3.5 mr-1 text-slate-500" />
                    {project.tasks_count || 0} Tasks
                  </span>
                  <span className="flex items-center">
                    <FolderCheck className="h-3.5 w-3.5 mr-1 text-emerald-500" />
                    {project.completed_count || 0} Done
                  </span>
                </div>

                <button className="text-indigo-400 hover:text-indigo-300 font-semibold flex items-center">
                  Open Workspace <ArrowUpRight className="h-3.5 w-3.5 ml-1" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
