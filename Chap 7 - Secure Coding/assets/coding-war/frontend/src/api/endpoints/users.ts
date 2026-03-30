import { apiClient } from '../client';
import type { 
  UserProfile,
  UpdateUserRequest,
  UserStatistics
} from '../../types/api';

export const usersAPI = {
  getById: (id: string) =>
    apiClient.get<UserProfile>(`/api/users/${id}`),

  update: (id: string, data: UpdateUserRequest) =>
    apiClient.put<{ message: string }>(`/api/users/${id}`, data),

  statistics: (id: string) =>
    apiClient.get<UserStatistics>(`/api/users/${id}/statistics`),
};
