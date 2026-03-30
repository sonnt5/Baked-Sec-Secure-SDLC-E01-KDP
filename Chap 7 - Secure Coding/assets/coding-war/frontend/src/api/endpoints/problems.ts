import { apiClient } from '../client';
import type { 
  Problem, 
  ProblemListResponse, 
  ProblemFilters 
} from '../../types/api';

export interface TestCaseItem {
  id: string;
  order_index: number;
  is_hidden: boolean;
  input: string;
  output: string;
  created_at: string;
}

export const problemsAPI = {
  list: (filters: ProblemFilters = {}) =>
    apiClient.get<ProblemListResponse>('/api/problems', { params: filters }),

  getById: (id: string) =>
    apiClient.get<Problem>(`/api/problems/${id}`),

  create: (data: Partial<Problem>) =>
    apiClient.post<any>('/api/problems', data),

  update: (id: string, data: Partial<Problem>) =>
    apiClient.put<{ message: string }>(`/api/problems/${id}`, data),

  delete: (id: string) =>
    apiClient.delete<{ message: string }>(`/api/problems/${id}`),

  // ─── Test Cases ───────────────────────────────────────────────────────────

  listTestCases: (id: string) =>
    apiClient.get<{ testCases: TestCaseItem[]; total: number }>(
      `/api/problems/${id}/test-cases`
    ),

  addTestCase: (id: string, input: string, output: string, isSample = false) =>
    apiClient.post<TestCaseItem>(`/api/problems/${id}/test-cases/single`, {
      input,
      output,
      is_sample: isSample,
    }),

  deleteTestCase: (problemId: string, tcId: string) =>
    apiClient.delete<void>(`/api/problems/${problemId}/test-cases/${tcId}`),

  uploadTestCases: (id: string, file: File, sampleCount: number = 0) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('sampleCount', String(sampleCount));
    return apiClient.post<{ message: string; testCasesCount: number }>(
      `/api/problems/${id}/test-cases`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  },
};
