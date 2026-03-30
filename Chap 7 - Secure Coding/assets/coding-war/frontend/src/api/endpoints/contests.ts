import { apiClient } from '../client';
import type { 
  Contest,
  ContestListResponse,
  ScoreboardResponse
} from '../../types/api';

export const contestsAPI = {
  list: (params?: { page?: number; limit?: number }) =>
    apiClient.get<ContestListResponse>('/api/contests', { params }),

  getById: (id: string) =>
    apiClient.get<Contest>(`/api/contests/${id}`),

  create: (data: Partial<Contest>) =>
    apiClient.post<{ contestId: string }>('/api/contests', data),

  register: (id: string) =>
    apiClient.post<{ message: string }>(`/api/contests/${id}/register`),

  updateProblems: (id: string, problems: { problemId: string; orderIndex?: number; points?: number }[]) =>
    apiClient.put<{ message: string }>(`/api/contests/${id}/problems`, problems),

  scoreboard: (id: string) =>
    apiClient.get<ScoreboardResponse>(`/api/contests/${id}/scoreboard`),
};
