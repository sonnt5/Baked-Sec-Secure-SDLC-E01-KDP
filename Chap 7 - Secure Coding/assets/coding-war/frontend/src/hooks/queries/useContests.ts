import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contestsAPI } from '../../api/endpoints/contests';
import type { Contest } from '../../types/api';

export function useContests(params?: { page?: number; limit?: number }) {
  return useQuery({
    queryKey: ['contests', params],
    queryFn: () => contestsAPI.list(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useContest(id: string) {
  return useQuery({
    queryKey: ['contest', id],
    queryFn: () => contestsAPI.getById(id),
    staleTime: 5 * 60 * 1000,
    enabled: !!id,
  });
}

export function useCreateContest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Contest>) => contestsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contests'] });
    },
  });
}

export function useRegisterContest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => contestsAPI.register(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['contest', id] });
      queryClient.invalidateQueries({ queryKey: ['contests'] });
    },
  });
}

export function useScoreboard(id: string) {
  return useQuery({
    queryKey: ['scoreboard', id],
    queryFn: () => contestsAPI.scoreboard(id),
    staleTime: 30 * 1000, // 30 seconds
    enabled: !!id,
  });
}
