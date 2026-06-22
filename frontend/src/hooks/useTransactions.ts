import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../api/client';
import type { TransactionPage } from '../types';

interface TransactionFilter {
  mode: string;
  start_date?: string;
  end_date?: string;
  category_id?: number;
  page?: number;
  page_size?: number;
}

export function useTransactions(filter: TransactionFilter) {
  const params: Record<string, string | number> = { mode: filter.mode };
  if (filter.start_date) params.start_date = filter.start_date;
  if (filter.end_date) params.end_date = filter.end_date;
  if (filter.category_id) params.category_id = filter.category_id;
  params.page = filter.page ?? 1;
  params.page_size = filter.page_size ?? 50;

  return useQuery<TransactionPage>({
    queryKey: ['transactions', filter],
    queryFn: () => client.get('/transactions', { params }).then((r) => r.data),
  });
}

export function useUpdateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ txnId, categoryId }: { txnId: number; categoryId: number | null }) =>
      client.patch(`/transactions/${txnId}/category`, null, { params: { category_id: categoryId } }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['transactions'] }),
  });
}
