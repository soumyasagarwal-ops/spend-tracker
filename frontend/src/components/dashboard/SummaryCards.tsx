import { formatCurrency } from '../../utils/formatters';
import type { AnalyticsSummary } from '../../types';
import LoadingSpinner from '../shared/LoadingSpinner';

interface Props {
  data?: AnalyticsSummary;
  isLoading: boolean;
}

interface CardProps {
  label: string;
  value: string;
  sub?: string;
  accent: string;
  icon: React.ReactNode;
}

function Card({ label, value, sub, accent, icon }: CardProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-5 flex items-start gap-4">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${accent}`}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">{label}</p>
        <p className="text-xl font-bold text-slate-800 truncate">{value}</p>
        {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

export default function SummaryCards({ data, isLoading }: Props) {
  const credits = data?.total_credits ?? 0;
  const spend = data?.total_spend ?? 0;
  const savingsRate = credits > 0 ? Math.round(((credits - spend) / credits) * 100) : null;

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-5 h-24 flex items-center justify-center">
            <LoadingSpinner />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      <Card
        label="Total Spend"
        value={formatCurrency(spend)}
        accent="bg-indigo-50"
        icon={<svg className="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-4H9l3-7 3 7h-2v4z" strokeLinecap="round" strokeLinejoin="round"/><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2" strokeLinecap="round"/></svg>}
      />
      <Card
        label="Total Income"
        value={formatCurrency(credits)}
        sub={savingsRate !== null && savingsRate > 0 ? `${savingsRate}% saved` : savingsRate !== null ? 'overspending' : undefined}
        accent="bg-emerald-50"
        icon={<svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" strokeLinecap="round" strokeLinejoin="round"/></svg>}
      />
      <Card
        label="Daily Average"
        value={formatCurrency(data?.daily_average ?? 0)}
        sub="per day"
        accent="bg-violet-50"
        icon={<svg className="w-5 h-5 text-violet-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18" strokeLinecap="round"/></svg>}
      />
      <Card
        label="Transactions"
        value={String(data?.transaction_count ?? 0)}
        accent="bg-sky-50"
        icon={<svg className="w-5 h-5 text-sky-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" strokeLinecap="round"/></svg>}
      />
      <Card
        label="Top Category"
        value={data?.top_category ?? '—'}
        accent="bg-amber-50"
        icon={<svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" strokeLinecap="round"/></svg>}
      />
    </div>
  );
}
