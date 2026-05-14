import { create } from "zustand"

interface UIState {
  isSidebarOpen: boolean
  toggleSidebar: () => void
  notifications: string[]
  addNotification: (msg: string) => void
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  notifications: [],
  addNotification: (msg) => set((state) => ({ 
    notifications: [...state.notifications, msg] 
  })),
}))
