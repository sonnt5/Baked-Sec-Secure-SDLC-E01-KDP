import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { problemsAPI } from '../../api/endpoints/problems';
import type { ProblemFilters, Problem } from '../../types/api';

export function useProblems(filters: ProblemFilters = {}) {
  return useQuery({
    queryKey: ['problems', filters],
    queryFn: () => problemsAPI.list(filters),
    staleTime: 0, // always refetch so userSolved stays current
  });
}

export function useProblem(id: string) {
  return useQuery({
    queryKey: ['problem', id],
    queryFn: () => problemsAPI.getById(id),
    staleTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!id,
  });
}

export function useCreateProblem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Problem>) => problemsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

export function useUpdateProblem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Problem> }) =>
      problemsAPI.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['problems'] });
      queryClient.invalidateQueries({ queryKey: ['problem', variables.id] });
    },
  });
}

export function useDeleteProblem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => problemsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

export function useUploadTestCases() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, file }: { id: string; file: File }) =>
      problemsAPI.uploadTestCases(id, file),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['problem', variables.id] });
    },
  });
}
