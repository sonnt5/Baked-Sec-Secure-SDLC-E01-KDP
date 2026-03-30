import { apiClient } from '../client';
import type { 
  LoginRequest, 
  LoginResponse, 
  RegisterRequest
} from '../../types/api';

export const authAPI = {
  register: (data: RegisterRequest) =>
    apiClient.post<{ message: string; userId: string }>('/api/auth/register', data),

  verifyEmail: (token: string) =>
    apiClient.post<{ message: string }>('/api/auth/verify-email', { token }),

  login: (data: LoginRequest) =>
    apiClient.post<LoginResponse>('/api/auth/login', data),

  refresh: (refreshToken: string) =>
    apiClient.post<{ accessToken: string }>('/api/auth/refresh', { refreshToken }),

  forgotPassword: (email: string) =>
    apiClient.post<{ message: string }>('/api/auth/forgot-password', { email }),

  resetPassword: (token: string, newPassword: string) =>
    apiClient.post<{ message: string }>('/api/auth/reset-password', { token, newPassword }),
};
