import { apiClient } from '../client';
import type { 
  AdminUserListResponse,
  AdminStatistics
} from '../../types/api';

export const adminAPI = {
  users: (params?: { page?: number; limit?: number; search?: string }) =>
    apiClient.get<AdminUserListResponse>('/api/admin/users', { params }),

  statistics: () =>
    apiClient.get<AdminStatistics>('/api/admin/statistics'),

  updateUserRole: (userId: string, role: string) =>
    apiClient.put<{ message: string }>(`/api/admin/users/${userId}/role`, { role }),
};
