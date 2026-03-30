import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosError } from 'axios';

class APIClient {
  private client: AxiosInstance;
  private refreshing: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor: attach JWT token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor: handle errors and token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Handle 401 Unauthorized - attempt token refresh
        // Skip refresh for auth endpoints (login, register, etc.)
        const isAuthEndpoint = originalRequest.url?.includes('/api/auth/login') ||
                               originalRequest.url?.includes('/api/auth/register') ||
                               originalRequest.url?.includes('/api/auth/refresh');

        if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshToken();
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed, clear auth and redirect to login
            this.clearAuth();
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
            return Promise.reject(refreshError);
          }
        }

        // Handle other errors
        this.handleError(error);
        return Promise.reject(error);
      }
    );
  }

  private async refreshToken(): Promise<string> {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshing) {
      return this.refreshing;
    }

    this.refreshing = (async () => {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'}/api/auth/refresh`,
          { refreshToken }
        );

        const { accessToken } = response.data;
        this.setAccessToken(accessToken);
        return accessToken;
      } catch (error) {
        this.clearAuth();
        throw error;
      }
    })();

    try {
      return await this.refreshing;
    } finally {
      this.refreshing = null;
    }
  }

  private handleError(error: AxiosError) {
    if (error.response) {
      // Server responded with error
      const status = error.response.status;
      const message = (error.response.data as any)?.message || 'An error occurred';

      // Log error for debugging
      console.error(`API Error [${status}]:`, message, error.response.data);

      // Handle specific status codes
      switch (status) {
        case 403:
          console.error('Forbidden: You do not have permission to access this resource');
          break;
        case 429: {
          const retryAfter = error.response.headers?.['retry-after'];
          console.warn(`Rate limited on ${error.config?.url}. Retry after: ${retryAfter || 'unknown'}s`);
          break;
        }
        case 500:
          console.error('Server Error: Something went wrong on the server');
          break;
      }
    } else if (error.request) {
      // Request made but no response
      console.error('Network error: Please check your connection', error.request);
    } else {
      // Something else happened
      console.error('An unexpected error occurred:', error.message);
    }
  }

  // Retry logic with exponential backoff
  private async retryRequest<T>(
    requestFn: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000
  ): Promise<T> {
    let lastError: any;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await requestFn();
      } catch (error) {
        lastError = error;
        
        // Don't retry on client errors (4xx) except 429 (rate limit)
        if (axios.isAxiosError(error) && error.response) {
          const status = error.response.status;
          if (status >= 400 && status < 500 && status !== 429) {
            throw error;
          }
        }

        // Calculate exponential backoff delay
        if (attempt < maxRetries - 1) {
          const delay = baseDelay * Math.pow(2, attempt);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError;
  }

  // Token management helpers
  private getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    const authData = localStorage.getItem('auth-storage');
    if (!authData) return null;
    try {
      const parsed = JSON.parse(authData);
      return parsed.state?.accessToken || null;
    } catch {
      return null;
    }
  }

  private getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    const authData = localStorage.getItem('auth-storage');
    if (!authData) return null;
    try {
      const parsed = JSON.parse(authData);
      return parsed.state?.refreshToken || null;
    } catch {
      return null;
    }
  }

  private setAccessToken(token: string): void {
    if (typeof window === 'undefined') return;
    const authData = localStorage.getItem('auth-storage');
    if (!authData) return;
    try {
      const parsed = JSON.parse(authData);
      if (parsed.state) {
        parsed.state.accessToken = token;
        localStorage.setItem('auth-storage', JSON.stringify(parsed));
      }
    } catch (error) {
      console.error('Failed to update access token:', error);
    }
  }

  private clearAuth(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('auth-storage');
  }

  // HTTP methods with retry logic
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.retryRequest(async () => {
      const response = await this.client.get<T>(url, config);
      return response.data;
    });
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.retryRequest(async () => {
      const response = await this.client.post<T>(url, data, config);
      return response.data;
    });
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.retryRequest(async () => {
      const response = await this.client.put<T>(url, data, config);
      return response.data;
    });
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.retryRequest(async () => {
      const response = await this.client.delete<T>(url, config);
      return response.data;
    });
  }
}

export const apiClient = new APIClient();
