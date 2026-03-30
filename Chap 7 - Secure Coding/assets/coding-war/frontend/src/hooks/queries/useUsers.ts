import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersAPI } from '../../api/endpoints/users';
import type { UpdateUserRequest } from '../../types/api';

export function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: () => usersAPI.getById(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!id,
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateUserRequest }) =>
      usersAPI.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['user', variables.id] });
    },
  });
}

export function useUserStatistics(id: string) {
  return useQuery({
    queryKey: ['user-statistics', id],
    queryFn: () => usersAPI.statistics(id),
    staleTime: 5 * 60 * 1000,
    enabled: !!id,
  });
}
