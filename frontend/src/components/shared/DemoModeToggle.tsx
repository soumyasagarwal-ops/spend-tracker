import { useDemoModeStore } from '../../store/demoMode';

export default function DemoModeToggle() {
  const { isDemoMode, toggle } = useDemoModeStore();

  return (
    <button
      onClick={toggle}
      className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium border transition-all ${
        isDemoMode
          ? 'bg-amber-100 border-amber-300 text-amber-800'
          : 'bg-slate-100 border-slate-300 text-slate-600 hover:bg-slate-200'
      }`}
    >
      <span
        className={`w-2 h-2 rounded-full ${isDemoMode ? 'bg-amber-500' : 'bg-slate-400'}`}
      />
      {isDemoMode ? 'Demo Mode' : 'Real Data'}
    </button>
  );
}
