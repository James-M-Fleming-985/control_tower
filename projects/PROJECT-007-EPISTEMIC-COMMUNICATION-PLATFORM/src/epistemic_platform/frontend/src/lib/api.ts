import axios from 'axios';
import { useAuthStore } from '@/stores/auth-store';
import type { TokenResponse } from '@/types/api';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401: try refresh, retry original request; if refresh fails → logout
let refreshPromise: Promise<string> | null = null;

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error);
    }
    original._retry = true;

    const store = useAuthStore.getState();
    if (!store.refreshToken) {
      store.logout();
      return Promise.reject(error);
    }

    // Deduplicate concurrent refresh calls
    if (!refreshPromise) {
      refreshPromise = (async () => {
        try {
          const { data } = await axios.post<TokenResponse>(
            '/api/auth/refresh',
            null,
            { params: { refresh_token: store.refreshToken } },
          );
          store.setTokens(data.access_token, data.refresh_token);
          return data.access_token;
        } catch {
          store.logout();
          throw error;
        } finally {
          refreshPromise = null;
        }
      })();
    }

    const newToken = await refreshPromise;
    original.headers.Authorization = `Bearer ${newToken}`;
    return api(original);
  },
);

export default api;
