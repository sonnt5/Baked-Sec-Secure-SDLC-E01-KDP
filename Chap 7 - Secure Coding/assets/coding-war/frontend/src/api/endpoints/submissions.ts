import { apiClient } from '../client';
import type { 
  CreateSubmissionRequest,
  Submission,
  SubmissionListResponse,
  SubmissionFilters
} from '../../types/api';

export const submissionsAPI = {
  create: (data: CreateSubmissionRequest) =>
    apiClient.post<{ submissionId: string }>('/api/submissions', data),

  getById: (id: string) =>
    apiClient.get<Submission>(`/api/submissions/${id}`),

  list: (filters: SubmissionFilters = {}) =>
    apiClient.get<SubmissionListResponse>('/api/submissions', { params: filters }),

  rejudge: (id: string) =>
    apiClient.post<{ message: string }>(`/api/submissions/${id}/rejudge`),
};
