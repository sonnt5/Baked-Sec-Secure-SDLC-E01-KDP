import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminAPI } from '../../api/endpoints/admin';

export function useAdminUsers(params?: { page?: number; limit?: number; search?: string }) {
  return useQuery({
    queryKey: ['admin-users', params],
    queryFn: () => adminAPI.users(params),
    staleTime: 2 * 60 * 1000,
  });
}

export function useAdminStatistics() {
  return useQuery({
    queryKey: ['admin-statistics'],
    queryFn: () => adminAPI.statistics(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useUpdateUserRole() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: string }) =>
      adminAPI.updateUserRole(userId, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
  });
}
