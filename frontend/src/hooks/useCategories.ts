import { useQuery } from '@tanstack/react-query';
import client from '../api/client';
import type { Category } from '../types';

export function useCategories() {
  return useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: () => client.get('/categories').then((r) => r.data),
    staleTime: 60_000,
  });
}
