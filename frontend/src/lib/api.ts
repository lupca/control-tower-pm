import axios from 'axios';

// Base Axios Instance
export const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types & Data Contracts
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'review' | 'done' | 'cancelled' | 'failed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  risk?: 'low' | 'medium' | 'high';
  executor?: string;
  reviewer?: string;
  project_id?: string;
  files?: string[];
  created_at?: string;
  updated_at?: string;
  deadline?: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'archived' | 'planning';
  tasks_count?: number;
  completed_count?: number;
  created_at?: string;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'idle' | 'busy' | 'offline' | 'error';
  current_task_id?: string;
  model?: string;
  last_active?: string;
  capabilities?: string[];
}

export interface SystemHealth {
  status: string;
  service: string;
  version?: string;
  timestamp?: string;
}

export interface AuditLog {
  id: string;
  task_id?: string;
  agent_id?: string;
  action: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

// API Methods
export const tasksApi = {
  getTasks: async (params?: { project_id?: string; status?: string; search?: string }): Promise<Task[]> => {
    try {
      const res = await api.get('/tasks', { params });
      return res.data;
    } catch {
      // Fallback empty list or mock response if backend route is unavailable
      return [];
    }
  },
  getTaskById: async (id: string): Promise<Task | null> => {
    try {
      const res = await api.get(`/tasks/${id}`);
      return res.data;
    } catch {
      return null;
    }
  },
  createTask: async (task: Partial<Task>): Promise<Task> => {
    const res = await api.post('/tasks', task);
    return res.data;
  },
  updateTask: async (id: string, updates: Partial<Task>): Promise<Task> => {
    const res = await api.patch(`/tasks/${id}`, updates);
    return res.data;
  },
  deleteTask: async (id: string): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },
};

export const projectsApi = {
  getProjects: async (): Promise<Project[]> => {
    try {
      const res = await api.get('/projects');
      return res.data;
    } catch {
      return [];
    }
  },
  getProjectById: async (id: string): Promise<Project | null> => {
    try {
      const res = await api.get(`/projects/${id}`);
      return res.data;
    } catch {
      return null;
    }
  },
};

export const agentsApi = {
  getAgents: async (): Promise<Agent[]> => {
    try {
      const res = await api.get('/agents');
      return res.data;
    } catch {
      return [];
    }
  },
};

export const healthApi = {
  getHealth: async (): Promise<SystemHealth> => {
    try {
      const res = await api.get('/health');
      return res.data;
    } catch {
      return { status: 'offline', service: 'control-tower-v2-backend' };
    }
  },
};
