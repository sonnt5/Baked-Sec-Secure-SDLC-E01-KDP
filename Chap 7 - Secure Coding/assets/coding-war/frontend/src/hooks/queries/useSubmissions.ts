import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { submissionsAPI } from '../../api/endpoints/submissions';
import type { CreateSubmissionRequest, SubmissionFilters } from '../../types/api';

export function useSubmissions(filters: SubmissionFilters = {}) {
  return useQuery({
    queryKey: ['submissions', filters],
    queryFn: () => submissionsAPI.list(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useSubmission(id: string) {
  return useQuery({
    queryKey: ['submission', id],
    queryFn: () => submissionsAPI.getById(id),
    enabled: !!id,
    refetchInterval: (query) => {
      // Poll every 2 seconds if status is not final
      const data = query.state.data;
      const finalStatuses = ['ACCEPTED', 'WRONG_ANSWER', 'TIME_LIMIT_EXCEEDED', 
                            'MEMORY_LIMIT_EXCEEDED', 'RUNTIME_ERROR', 'COMPILATION_ERROR'];
      return data && data.status && finalStatuses.includes(data.status) ? false : 2000;
    },
  });
}

export function useSubmitSolution() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateSubmissionRequest) => submissionsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
    },
  });
}

export function useRejudgeSubmission() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => submissionsAPI.rejudge(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['submission', id] });
      queryClient.invalidateQueries({ queryKey: ['submissions'] });
    },
  });
}
