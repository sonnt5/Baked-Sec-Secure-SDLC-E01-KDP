import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types/api';
import apiClient from '../api/client';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  _hasHydrated: boolean;

  setUser: (user: User) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setAccessToken: (accessToken: string) => void;
  setHasHydrated: (value: boolean) => void;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      _hasHydrated: false,

      setHasHydrated: (value) => set({ _hasHydrated: value }),

      setUser: (user) => set({ user, isAuthenticated: true }),

      setTokens: (accessToken, refreshToken) =>
        set({ accessToken, refreshToken, isAuthenticated: true }),

      setAccessToken: (accessToken) => set({ accessToken }),

      // Gap fix #4 (frontend): Call POST /auth/logout to revoke the refresh token
      // in Redis before clearing local state — prevents reuse after logout.
      logout: async () => {
        const { refreshToken } = get();
        if (refreshToken) {
          try {
            await apiClient.post('/auth/logout', { refresh_token: refreshToken });
          } catch {
            // Fire-and-forget: always clear local state even if server call fails
          }
        }
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
      onRehydrateStorage: () => (state) => {
        if (state && state.user && state.accessToken) {
          state.isAuthenticated = true;
        }
        state?.setHasHydrated(true);
      },
    }
  )
);
