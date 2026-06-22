import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
} from 'recharts';
import { formatCurrency } from '../../utils/formatters';
import type { CategorySpend } from '../../types';
import LoadingSpinner from '../shared/LoadingSpinner';

interface Props {
  data?: CategorySpend[];
  isLoading: boolean;
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload?.length) {
    const d = payload[0].payload as CategorySpend;
    return (
      <div className="bg-white border border-slate-100 rounded-xl px-4 py-3 shadow-lg text-sm">
        <p className="font-semibold text-slate-800 mb-0.5">{d.category}</p>
        <p className="text-slate-600">{formatCurrency(d.total)}</p>
        <p className="text-slate-400 text-xs">{d.percentage}% of total</p>
      </div>
    );
  }
  return null;
};

export default function CategoryPieChart({ data, isLoading }: Props) {
  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
      <div className="mb-5">
        <h3 className="text-sm font-semibold text-slate-800">Spend by Category</h3>
        <p className="text-xs text-slate-400 mt-0.5">Breakdown for selected period</p>
      </div>
      {isLoading ? (
        <div className="flex items-center justify-center h-52"><LoadingSpinner size="lg" /></div>
      ) : !data?.length ? (
        <div className="flex flex-col items-center justify-center h-52 text-slate-300 gap-2">
          <svg width="32" height="32" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"/><path d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"/></svg>
          <span className="text-sm">No data for this period</span>
        </div>
      ) : (
        <div className="flex flex-col lg:flex-row items-center gap-6">
          <div className="flex-shrink-0">
            <ResponsiveContainer width={200} height={200}>
              <PieChart>
                <Pie
                  data={data}
                  dataKey="total"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  strokeWidth={0}
                >
                  {data.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex-1 w-full">
            <div className="space-y-2.5">
              {data.map((entry) => (
                <div key={entry.category} className="flex items-center gap-3">
                  <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: entry.color }} />
                  <span className="text-sm text-slate-600 flex-1 truncate">{entry.category}</span>
                  <span className="text-sm font-semibold text-slate-800 tabular-nums">{formatCurrency(entry.total)}</span>
                  <span className="text-xs text-slate-400 w-10 text-right tabular-nums">{entry.percentage}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
