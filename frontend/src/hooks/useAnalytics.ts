import { useQuery } from '@tanstack/react-query';
import client from '../api/client';
import type {
  AnalyticsSummary, TimeSeriesPoint, CategorySpend, InsightItem,
  WeeklyVelocityPoint, HeatmapCell, MerchantSpend, RecurringTransaction,
  IncomeMonthPoint, IncomeSource, SavingsPoint, WalletSummary,
} from '../types';

interface DateRange {
  start?: string;
  end?: string;
}

function buildParams(mode: string, range?: DateRange) {
  const p: Record<string, string> = { mode };
  if (range?.start) p.start_date = range.start;
  if (range?.end) p.end_date = range.end;
  return p;
}

export function useSummary(mode: string, range?: DateRange) {
  return useQuery<AnalyticsSummary>({
    queryKey: ['analytics', 'summary', mode, range],
    queryFn: () => client.get('/analytics/summary', { params: buildParams(mode, range) }).then((r) => r.data),
  });
}

export function useWallet(mode: string, range?: DateRange) {
  return useQuery<WalletSummary>({
    queryKey: ['analytics', 'wallet', mode, range],
    queryFn: () => client.get('/analytics/wallet', { params: buildParams(mode, range) }).then((r) => r.data),
  });
}

export function useByDay(mode: string, range?: DateRange) {
  return useQuery<TimeSeriesPoint[]>({
    queryKey: ['analytics', 'by-day', mode, range],
    queryFn: () => client.get('/analytics/by-day', { params: buildParams(mode, range) }).then((r) => r.data),
  });
}

export function useByMonth(mode: string, range?: DateRange) {
  return useQuery<TimeSeriesPoint[]>({
    queryKey: ['analytics', 'by-month', mode, range],
    queryFn: () => client.get('/analytics/by-month', { params: buildParams(mode, range) }).then((r) => r.data),
  });
}

export function useByYear(mode: string) {
  return useQuery<TimeSeriesPoint[]>({
    queryKey: ['analytics', 'by-year', mode],
    queryFn: () => client.get('/analytics/by-year', { params: { mode } }).then((r) => r.data),
  });
}

export function useByCategory(mode: string, range?: DateRange) {
  return useQuery<CategorySpend[]>({
    queryKey: ['analytics', 'by-category', mode, range],
    queryFn: () => client.get('/analytics/by-category', { params: buildParams(mode, range) }).then((r) => r.data),
  });
}

export function useInsights(mode: string, range?: DateRange) {
  return useQuery<InsightItem[]>({
    queryKey: ['analytics', 'insights', mode, range],
    queryFn: () => client.get('/analytics/insights', { params: buildParams(mode, range) }).then((r) => r.data),
  });
}

export function useWeeklyVelocity(mode: string, range?: DateRange) {
  return useQuery<WeeklyVelocityPoint[]>({
    queryKey: ['analytics', 'weekly-velocity', mode, range],
    queryFn: () => client.get('/analytics/weekly-velocity', { params: buildParams(mode, range) }).then((r) => r.data),
  });
}

export function useHeatmap(mode: string) {
  return useQuery<HeatmapCell[]>({
    queryKey: ['analytics', 'heatmap', mode],
    queryFn: () => client.get('/analytics/heatmap', { params: { mode } }).then((r) => r.data),
  });
}

export function useTopMerchants(mode: string, range?: DateRange) {
  return useQuery<MerchantSpend[]>({
    queryKey: ['analytics', 'top-merchants', mode, range],
    queryFn: () => client.get('/analytics/top-merchants', { params: buildParams(mode, range) }).then((r) => r.data),
  });
}

export function useRecurring(mode: string) {
  return useQuery<RecurringTransaction[]>({
    queryKey: ['analytics', 'recurring', mode],
    queryFn: () => client.get('/analytics/recurring', { params: { mode } }).then((r) => r.data),
  });
}

export function useIncomeMonthly(mode: string) {
  return useQuery<IncomeMonthPoint[]>({
    queryKey: ['analytics', 'income-monthly', mode],
    queryFn: () => client.get('/analytics/income-monthly', { params: { mode } }).then((r) => r.data),
  });
}

export function useIncomeSources(mode: string, range?: DateRange) {
  return useQuery<IncomeSource[]>({
    queryKey: ['analytics', 'income-sources', mode, range],
    queryFn: () => client.get('/analytics/income-sources', { params: buildParams(mode, range) }).then((r) => r.data),
  });
}

export function useSavingsTrajectory(mode: string) {
  return useQuery<SavingsPoint[]>({
    queryKey: ['analytics', 'savings-trajectory', mode],
    queryFn: () => client.get('/analytics/savings-trajectory', { params: { mode } }).then((r) => r.data),
  });
}
