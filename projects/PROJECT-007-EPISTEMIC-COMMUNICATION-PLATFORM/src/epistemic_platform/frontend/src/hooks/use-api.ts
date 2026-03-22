import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import type {
  ActorProfile,
  ScenarioDefinition,
  ConversationSession,
  ConversationSessionSummary,
  ConversationSessionCreate,
  AssessmentQuestion,
  GamificationProfile,
  ProficiencyProfile,
  GrowthReport,
  Milestone,
  SessionAnalysis,
  UserProfile,
  UserProfileUpdate,
} from '@/types/api';

// ─── Actors ──────────────────────────────────────────────────────────────────
export function useActors() {
  return useQuery({
    queryKey: ['actors'],
    queryFn: () => api.get<ActorProfile[]>('/actors/').then((r) => r.data),
  });
}

export function useActor(id: number | string) {
  return useQuery({
    queryKey: ['actors', id],
    queryFn: () => api.get<ActorProfile>(`/actors/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

// ─── Scenarios ───────────────────────────────────────────────────────────────
export function useScenarios(params?: { category?: string; difficulty?: string }) {
  return useQuery({
    queryKey: ['scenarios', params],
    queryFn: () => api.get<ScenarioDefinition[]>('/scenarios/', { params }).then((r) => r.data),
  });
}

export function useScenario(id: number | string) {
  return useQuery({
    queryKey: ['scenarios', id],
    queryFn: () => api.get<ScenarioDefinition>(`/scenarios/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

// ─── Sessions ────────────────────────────────────────────────────────────────
export function useSessions() {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: () => api.get<ConversationSessionSummary[]>('/sessions/').then((r) => r.data),
  });
}

export function useSession(id: number | string) {
  return useQuery({
    queryKey: ['sessions', id],
    queryFn: () => api.get<ConversationSession>(`/sessions/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCreateSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ConversationSessionCreate) =>
      api.post<ConversationSession>('/sessions/', data).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sessions'] }),
  });
}

export function useEndSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      api.post<ConversationSession>(`/sessions/${id}/end`).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sessions'] }),
  });
}

// ─── Assessment ──────────────────────────────────────────────────────────────
export function useAssessmentQuestions() {
  return useQuery({
    queryKey: ['assessment-questions'],
    queryFn: () =>
      api.get<{ questions: AssessmentQuestion[] }>('/assessment/questions').then((r) => r.data),
  });
}

export function useSubmitAssessment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { answers: Record<string, string> }) =>
      api.post<Record<string, unknown>>('/assessment/evaluate', data).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['user'] }),
  });
}

// ─── Gamification ────────────────────────────────────────────────────────────
export function useGamificationProfile() {
  return useQuery({
    queryKey: ['gamification', 'profile'],
    queryFn: () => api.get<GamificationProfile>('/gamification/profile').then((r) => r.data),
  });
}

export function useProficiency() {
  return useQuery({
    queryKey: ['gamification', 'proficiency'],
    queryFn: () => api.get<ProficiencyProfile>('/gamification/proficiency').then((r) => r.data),
  });
}

export function useGrowth() {
  return useQuery({
    queryKey: ['gamification', 'growth'],
    queryFn: () => api.get<GrowthReport>('/gamification/growth').then((r) => r.data),
  });
}

export function useMilestones() {
  return useQuery({
    queryKey: ['gamification', 'milestones'],
    queryFn: () => api.get<{ milestones: Milestone[] }>('/gamification/milestones').then((r) => r.data),
  });
}

// ─── Analytics ───────────────────────────────────────────────────────────────
export function useSessionAnalysis(sessionId: number | string) {
  return useQuery({
    queryKey: ['analytics', 'session', sessionId],
    queryFn: () => api.get<SessionAnalysis>(`/analytics/session/${sessionId}`).then((r) => r.data),
    enabled: !!sessionId,
  });
}

export function useStanceInsights() {
  return useQuery({
    queryKey: ['analytics', 'stance-insights'],
    queryFn: () => api.get('/analytics/stance-insights').then((r) => r.data),
  });
}

// ─── User ────────────────────────────────────────────────────────────────────
export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UserProfileUpdate) =>
      api.patch<UserProfile>('/users/me', data).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['user'] }),
  });
}
