import { useMutation } from '@tanstack/react-query';
import { authAPI } from '../../api/endpoints/auth';
import type { LoginRequest, RegisterRequest } from '../../types/api';

export function useLogin() {
  return useMutation({
    mutationFn: (data: LoginRequest) => authAPI.login(data),
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (data: RegisterRequest) => authAPI.register(data),
  });
}

export function useVerifyEmail() {
  return useMutation({
    mutationFn: (token: string) => authAPI.verifyEmail(token),
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: (email: string) => authAPI.forgotPassword(email),
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: ({ token, newPassword }: { token: string; newPassword: string }) =>
      authAPI.resetPassword(token, newPassword),
  });
}
