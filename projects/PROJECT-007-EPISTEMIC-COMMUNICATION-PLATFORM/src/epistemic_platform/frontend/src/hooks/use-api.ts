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
  SyllabusProgress,
  UserProfile,
  UserProfileUpdate,
} from '@/types/api';

// ─── Client Config ───────────────────────────────────────────────────────────
interface ClientConfig {
  avatar_service_url: string | null;
  avatar_mode: 'static' | 'heygen' | 'self_hosted';
  heygen_available: boolean;
}

export function useClientConfig() {
  return useQuery({
    queryKey: ['client-config'],
    queryFn: () => api.get<ClientConfig>('/client-config').then((r) => r.data),
    staleTime: 5 * 60 * 1000, // 5 min — config rarely changes
  });
}

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

export function useSyllabus() {
  return useQuery({
    queryKey: ['gamification', 'syllabus'],
    queryFn: () => api.get<SyllabusProgress>('/gamification/syllabus').then((r) => r.data),
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

// ─── Avatar Lab (Admin) ──────────────────────────────────────────────────────

export interface AvatarAssignment {
  actor_id: number;
  actor_name: string;
  heygen_avatar_id: string | null;
  heygen_avatar_name: string | null;
  heygen_preview_url: string | null;
  auto_assigned: boolean;
}

export interface StockAvatar {
  avatar_id: string;
  avatar_name: string;
  gender: string;
  preview_image_url: string;
}

export function useAvatarAssignments() {
  return useQuery({
    queryKey: ['avatar', 'assignments'],
    queryFn: () => api.get<AvatarAssignment[]>('/avatar/assignments').then((r) => r.data),
  });
}

export function useStockLibrary() {
  return useQuery({
    queryKey: ['avatar', 'stock-library'],
    queryFn: () => api.get<StockAvatar[]>('/avatar/stock-library').then((r) => r.data),
    enabled: false, // manual fetch only
  });
}

export function useManualAssignAvatar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ actorId, avatarId }: { actorId: number; avatarId: string }) =>
      api.put(`/avatar/${actorId}/assign`, { heygen_avatar_id: avatarId }).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['avatar', 'assignments'] }),
  });
}

export function useRemoveAvatarAssignment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (actorId: number) =>
      api.delete(`/avatar/${actorId}/assign`).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['avatar', 'assignments'] }),
  });
}

export function useReassignAllAvatars() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => api.post('/avatar/assign').then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['avatar', 'assignments'] }),
  });
}
