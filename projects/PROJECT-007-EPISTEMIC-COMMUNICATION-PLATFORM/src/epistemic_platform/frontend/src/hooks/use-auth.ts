import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/auth-store';
import api from '@/lib/api';
import type { UserProfile, TokenResponse, LoginRequest, RegisterRequest } from '@/types/api';

export function useAuth() {
  const { user, isAuthenticated, login, logout, setUser } = useAuthStore();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch user profile on mount if we have a token but no user
  useEffect(() => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken && !user) {
      api.get<UserProfile>('/users/me').then(
        (res) => setUser(res.data),
        () => logout(),
      );
    }
  }, [user, setUser, logout]);

  async function handleLogin(credentials: LoginRequest) {
    setLoading(true);
    setError(null);
    try {
      const { data: tokens } = await api.post<TokenResponse>('/auth/login', credentials);
      const store = useAuthStore.getState();
      store.setTokens(tokens.access_token, tokens.refresh_token);
      const { data: profile } = await api.get<UserProfile>('/users/me');
      login(profile, tokens.access_token, tokens.refresh_token);
      navigate(profile.assessment_history.length ? '/actors' : '/assessment');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Login failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(data: RegisterRequest) {
    setLoading(true);
    setError(null);
    try {
      await api.post('/auth/register', data);
      await handleLogin({ email: data.email, password: data.password });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Registration failed';
      setError(msg);
      setLoading(false);
    }
  }

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return { user, isAuthenticated, handleLogin, handleRegister, handleLogout, loading, error };
}
