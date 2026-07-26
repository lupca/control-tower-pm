import React, { useState } from 'react';
import { useParams, NavLink } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { tasksApi } from '../lib/api';
import {
  ArrowLeft,
  FileCode,
  Send,
  Bot,
  Terminal
} from 'lucide-react';

export const TaskDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [chatInput, setChatInput] = useState('');
  const [activeTab, setActiveTab] = useState<'details' | 'logs' | 'chat'>('details');

  const { data: task, isLoading } = useQuery({
    queryKey: ['task', id],
    queryFn: () => (id ? tasksApi.getTaskById(id) : null),
    enabled: !!id,
  });

  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'agent'; text: string; time: string }>>([
    {
      sender: 'agent',
      text: `Initialized environment context for task ${id || 'unknown'}. Ready for execution instructions.`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = {
      sender: 'user' as const,
      text: chatInput,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setChatInput('');

    // Mock agent response echo
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'agent' as const,
          text: `Acknowledged request: "${userMsg.text}". Processing task step...`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    }, 1000);
  };

  if (isLoading) {
    return <div className="p-12 text-center text-slate-400 text-xs">Loading task details...</div>;
  }

  const taskData = task || {
    id: id || 'CTV2-015',
    title: 'Frontend Setup - React + Vite + Tailwind',
    description: 'Setup React frontend replacing Streamlit dashboard + Chainlit chat.',
    status: 'in_progress' as const,
    priority: 'high' as const,
    risk: 'low' as const,
    executor: 'Antigravity Agent',
    reviewer: 'Code Reviewer',
    deadline: '2026-07-29',
    files: ['frontend/package.json', 'frontend/vite.config.ts', 'frontend/src/App.tsx'],
  };

  return (
    <div className="space-y-6">
      {/* Back Button & Header */}
      <div className="flex items-center space-x-3">
        <NavLink
          to="/tasks"
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
        </NavLink>
        <div>
          <div className="flex items-center space-x-3">
            <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
              {taskData.id}
            </span>
            <h1 className="text-xl font-bold tracking-tight text-white">{taskData.title}</h1>
          </div>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="flex border-b border-slate-800 space-x-4 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('details')}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === 'details'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Task Overview
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={`pb-3 border-b-2 transition-colors flex items-center space-x-1.5 ${
            activeTab === 'chat'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Bot className="h-3.5 w-3.5" />
          <span>Agent Chat</span>
        </button>
        <button
          onClick={() => setActiveTab('logs')}
          className={`pb-3 border-b-2 transition-colors flex items-center space-x-1.5 ${
            activeTab === 'logs'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Terminal className="h-3.5 w-3.5" />
          <span>Execution Logs</span>
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === 'details' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Task Card */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass-panel p-6 rounded-2xl space-y-4">
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider text-[11px]">
                Description & Context
              </h3>
              <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">
                {taskData.description || 'No description provided.'}
              </p>

              {taskData.files && taskData.files.length > 0 && (
                <div className="pt-4 border-t border-slate-800/80 space-y-2">
                  <h4 className="text-xs font-bold text-slate-300 flex items-center">
                    <FileCode className="h-4 w-4 mr-1.5 text-indigo-400" />
                    Target Files
                  </h4>
                  <ul className="space-y-1 text-xs font-mono text-slate-400">
                    {taskData.files.map((file, idx) => (
                      <li key={idx} className="p-2 rounded-lg bg-slate-950/60 border border-slate-800">
                        {file}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar Metadata */}
          <div className="space-y-6">
            <div className="glass-panel p-5 rounded-2xl space-y-4">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Metadata & Ownership
              </h3>

              <div className="space-y-3 text-xs">
                <div className="flex items-center justify-between py-2 border-b border-slate-800/60">
                  <span className="text-slate-400">Status</span>
                  <span className="px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 capitalize font-medium">
                    {taskData.status.replace('_', ' ')}
                  </span>
                </div>

                <div className="flex items-center justify-between py-2 border-b border-slate-800/60">
                  <span className="text-slate-400">Priority</span>
                  <span className="font-semibold text-slate-200 capitalize">{taskData.priority}</span>
                </div>

                <div className="flex items-center justify-between py-2 border-b border-slate-800/60">
                  <span className="text-slate-400">Risk Level</span>
                  <span className="font-semibold text-slate-200 capitalize">{taskData.risk || 'Low'}</span>
                </div>

                <div className="flex items-center justify-between py-2 border-b border-slate-800/60">
                  <span className="text-slate-400">Executor</span>
                  <span className="text-indigo-400 font-medium">{taskData.executor || 'Unassigned'}</span>
                </div>

                <div className="flex items-center justify-between py-2 border-b border-slate-800/60">
                  <span className="text-slate-400">Reviewer</span>
                  <span className="text-slate-300">{taskData.reviewer || 'Unassigned'}</span>
                </div>

                <div className="flex items-center justify-between py-2">
                  <span className="text-slate-400">Deadline</span>
                  <span className="text-slate-300">{taskData.deadline || 'None'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'chat' && (
        <div className="glass-panel rounded-2xl h-[500px] flex flex-col overflow-hidden">
          {/* Chat Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-md p-3.5 rounded-2xl text-xs space-y-1 ${
                    msg.sender === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-none'
                      : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none'
                  }`}
                >
                  <p>{msg.text}</p>
                  <span className="block text-[10px] text-slate-400 text-right">{msg.time}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="p-3 bg-slate-950 border-t border-slate-800 flex items-center space-x-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Send instruction or prompt to agent..."
              className="flex-1 px-4 py-2 text-xs bg-slate-900 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              className="p-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      )}

      {activeTab === 'logs' && (
        <div className="glass-panel p-4 rounded-2xl bg-slate-950 font-mono text-xs text-slate-300 space-y-2 h-[450px] overflow-y-auto">
          <p className="text-slate-500">[SYSTEM] Task session started for {taskData.id}</p>
          <p className="text-indigo-400">[AGENT] Reading specification file CTV2-015-frontend-setup.md</p>
          <p className="text-emerald-400">[BUILD] package.json generated with React 19 + Vite + Tailwind</p>
          <p className="text-slate-400">[LOG] Vite dev server configuration initialized on port 3000</p>
          <p className="text-emerald-400">[READY] Waiting for user actions...</p>
        </div>
      )}
    </div>
  );
};
