import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { agentsApi } from '../lib/api';
import { Bot, Cpu, Zap, Activity, CheckCircle2 } from 'lucide-react';

export const AgentsPage: React.FC = () => {
  const { data: agents = [], isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsApi.getAgents(),
  });

  const defaultAgents = [
    {
      id: 'antigravity-core',
      name: 'Antigravity Primary Agent',
      role: 'Full-stack Autonomous Engineer',
      status: 'busy',
      model: 'Gemini 3.6 Flash / Pro',
      current_task_id: 'CTV2-015',
      capabilities: ['Code Generation', 'Refactoring', 'System Testing', 'Docker Build'],
    },
    {
      id: 'code-reviewer',
      name: 'Code Reviewer Subagent',
      role: 'Quality Assurance & Security Auditor',
      status: 'idle',
      model: 'Claude 3.5 Sonnet',
      capabilities: ['AST Linting', 'Security Audit', 'Performance Optimization'],
    },
  ];

  const agentList = agents.length > 0 ? agents : defaultAgents;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center">
            <Bot className="h-6 w-6 mr-2 text-indigo-400" />
            Autonomous Agents
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Monitor registered subagent tools, active models, and operational metrics.
          </p>
        </div>
      </div>

      {/* Agents Grid */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading agents...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {agentList.map((agent) => (
            <div
              key={agent.id}
              className="glass-panel p-6 rounded-2xl space-y-4 border border-slate-800 hover:border-indigo-500/40 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="h-11 w-11 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <Bot className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">{agent.name}</h3>
                    <p className="text-xs text-slate-400">{agent.role}</p>
                  </div>
                </div>

                <span
                  className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${
                    agent.status === 'busy'
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'
                      : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  }`}
                >
                  <Activity className="h-3 w-3 mr-1" />
                  {agent.status}
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between py-1.5 border-b border-slate-800/60">
                  <span className="text-slate-400 flex items-center">
                    <Cpu className="h-3.5 w-3.5 mr-1.5 text-slate-500" /> Model Architecture
                  </span>
                  <span className="font-mono text-slate-200">{agent.model || 'LLM Engine'}</span>
                </div>

                {agent.current_task_id && (
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800/60">
                    <span className="text-slate-400 flex items-center">
                      <Zap className="h-3.5 w-3.5 mr-1.5 text-amber-400" /> Executing Task
                    </span>
                    <span className="font-mono font-bold text-indigo-400">{agent.current_task_id}</span>
                  </div>
                )}
              </div>

              {agent.capabilities && agent.capabilities.length > 0 && (
                <div className="pt-2">
                  <span className="text-[11px] font-bold text-slate-400 block mb-2 uppercase tracking-wider">
                    Capabilities
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {agent.capabilities.map((cap, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-300 flex items-center"
                      >
                        <CheckCircle2 className="h-3 w-3 mr-1 text-indigo-400" />
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
