import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface UserPreferences {
  theme: 'dark' | 'light';
  compactView: boolean;
  autoRefresh: boolean;
  refreshInterval: number; // in ms
  notificationsEnabled: boolean;
}

export interface UIStore {
  // Theme & Preferences
  preferences: UserPreferences;
  setTheme: (theme: 'dark' | 'light') => void;
  toggleTheme: () => void;
  updatePreferences: (prefs: Partial<UserPreferences>) => void;

  // Sidebar
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;

  // Active Project & Filters
  activeProjectId: string | null;
  setActiveProject: (id: string | null) => void;

  // Open Side Panels / Modals
  openPanels: Record<string, boolean>;
  togglePanel: (panelId: string) => void;
  openPanel: (panelId: string) => void;
  closePanel: (panelId: string) => void;

  // Active Task Detail
  activeTaskDetailId: string | null;
  setActiveTaskDetailId: (id: string | null) => void;
}

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      preferences: {
        theme: 'dark',
        compactView: false,
        autoRefresh: true,
        refreshInterval: 10000,
        notificationsEnabled: true,
      },
      setTheme: (theme) =>
        set((state) => ({
          preferences: { ...state.preferences, theme },
        })),
      toggleTheme: () =>
        set((state) => {
          const nextTheme = state.preferences.theme === 'dark' ? 'light' : 'dark';
          if (typeof document !== 'undefined') {
            if (nextTheme === 'dark') {
              document.documentElement.classList.add('dark');
            } else {
              document.documentElement.classList.remove('dark');
            }
          }
          return { preferences: { ...state.preferences, theme: nextTheme } };
        }),
      updatePreferences: (prefs) =>
        set((state) => ({
          preferences: { ...state.preferences, ...prefs },
        })),

      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      activeProjectId: null,
      setActiveProject: (id) => set({ activeProjectId: id }),

      openPanels: {},
      togglePanel: (panelId) =>
        set((state) => ({
          openPanels: {
            ...state.openPanels,
            [panelId]: !state.openPanels[panelId],
          },
        })),
      openPanel: (panelId) =>
        set((state) => ({
          openPanels: { ...state.openPanels, [panelId]: true },
        })),
      closePanel: (panelId) =>
        set((state) => ({
          openPanels: { ...state.openPanels, [panelId]: false },
        })),

      activeTaskDetailId: null,
      setActiveTaskDetailId: (id) => set({ activeTaskDetailId: id }),
    }),
    {
      name: 'control-tower-ui-storage',
      partialize: (state) => ({
        preferences: state.preferences,
        sidebarOpen: state.sidebarOpen,
        activeProjectId: state.activeProjectId,
      }),
    }
  )
);
