import type { InsightItem } from '../../types';
import LoadingSpinner from '../shared/LoadingSpinner';

interface Props {
  data?: InsightItem[];
  isLoading: boolean;
}

const TYPE_CONFIG = {
  warning: {
    bg: 'bg-amber-50',
    border: 'border-amber-100',
    icon: (
      <svg className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
      </svg>
    ),
    titleColor: 'text-amber-800',
    bodyColor: 'text-amber-700',
  },
  tip: {
    bg: 'bg-blue-50',
    border: 'border-blue-100',
    icon: (
      <svg className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
    titleColor: 'text-blue-800',
    bodyColor: 'text-blue-700',
  },
  info: {
    bg: 'bg-slate-50',
    border: 'border-slate-100',
    icon: (
      <svg className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    titleColor: 'text-slate-700',
    bodyColor: 'text-slate-600',
  },
  positive: {
    bg: 'bg-emerald-50',
    border: 'border-emerald-100',
    icon: (
      <svg className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    titleColor: 'text-emerald-800',
    bodyColor: 'text-emerald-700',
  },
};

function InsightCard({ item }: { item: InsightItem }) {
  const cfg = TYPE_CONFIG[item.type] ?? TYPE_CONFIG.info;
  return (
    <div className={`${cfg.bg} border ${cfg.border} rounded-xl p-4 flex gap-3`}>
      {cfg.icon}
      <div className="min-w-0">
        <p className={`text-sm font-semibold ${cfg.titleColor} mb-0.5`}>{item.title}</p>
        <p className={`text-xs leading-relaxed ${cfg.bodyColor}`}>{item.body}</p>
      </div>
    </div>
  );
}

export default function InsightsPanel({ data, isLoading }: Props) {
  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
      <div className="mb-5">
        <h3 className="text-sm font-semibold text-slate-800">Smart Insights</h3>
        <p className="text-xs text-slate-400 mt-0.5">Where you can save money this period</p>
      </div>
      {isLoading ? (
        <div className="flex items-center justify-center h-32"><LoadingSpinner size="lg" /></div>
      ) : !data?.length ? (
        <div className="flex flex-col items-center justify-center h-32 text-slate-300 gap-2">
          <svg width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <span className="text-sm">No insights for this period</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {data.map((item, i) => (
            <InsightCard key={i} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
