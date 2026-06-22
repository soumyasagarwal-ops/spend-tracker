import { create } from 'zustand';

interface DemoModeStore {
  isDemoMode: boolean;
  toggle: () => void;
  setDemoMode: (val: boolean) => void;
}

export const useDemoModeStore = create<DemoModeStore>((set) => ({
  isDemoMode: false,
  toggle: () => set((state) => ({ isDemoMode: !state.isDemoMode })),
  setDemoMode: (val) => set({ isDemoMode: val }),
}));

export const useMode = () => useDemoModeStore((s) => (s.isDemoMode ? 'demo' : 'real'));
