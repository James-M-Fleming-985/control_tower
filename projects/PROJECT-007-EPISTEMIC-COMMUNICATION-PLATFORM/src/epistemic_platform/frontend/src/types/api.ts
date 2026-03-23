// ─── Auth ────────────────────────────────────────────────────────────────────
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  display_name: string;
  password: string;
}

// ─── User Profile ────────────────────────────────────────────────────────────
export interface UserProfile {
  id: number;
  email: string;
  display_name: string;
  skill_level: string;
  preferences: Record<string, unknown>;
  assessment_history: AssessmentResult[];
  is_active: boolean;
  xp: number;
  level: number;
  achievements: Achievement[];
  subscription_tier: string;
  created_at: string;
  updated_at: string;
}

export interface UserProfileUpdate {
  display_name?: string;
  skill_level?: string;
  preferences?: Record<string, unknown>;
}

// ─── Actor Profile ───────────────────────────────────────────────────────────
export interface ActorProfile {
  id: number;
  name: string;
  description: string | null;
  epistemological_stance: string;
  ontology_config: OntologyConfig;
  archetype: string | null;
  is_active: boolean;
  avatar_config: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface OntologyConfig {
  stance: string;
  register: string;
  difficulty_modifier: number;
  custom_instructions: string;
  topics: string[];
  [key: string]: unknown;
}

// ─── Scenario Definition ─────────────────────────────────────────────────────
export interface ScenarioDefinition {
  id: number;
  title: string;
  description: string | null;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  actor_id: number | null;
  objectives: ScenarioObjective[];
  evaluation_criteria: EvaluationCriterion[];
  category: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ScenarioObjective {
  description: string;
  type: string;
  [key: string]: unknown;
}

export interface EvaluationCriterion {
  name: string;
  description: string;
  [key: string]: unknown;
}

// ─── Conversation Session ────────────────────────────────────────────────────
export interface ConversationSession {
  id: number;
  user_id: number;
  actor_id: number;
  scenario_id: number | null;
  status: 'active' | 'completed' | 'ended';
  mode: 'text' | 'voice';
  messages: ChatMessage[];
  coaching_annotations: CoachingAnnotation[];
  trilemma_state: TrilemmaState;
  turn_count: number;
  started_at: string;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationSessionSummary {
  id: number;
  actor_id: number;
  status: string;
  mode: string;
  turn_count: number;
  started_at: string;
  ended_at: string | null;
}

export interface ConversationSessionCreate {
  actor_id: number;
  scenario_id?: number;
  mode?: 'text' | 'voice';
}

// ─── Chat Messages ───────────────────────────────────────────────────────────
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface CoachingAnnotation {
  type: 'trilemma' | 'gricean' | 'stance' | 'general';
  coaching_type?: string;
  content: string;
  suggestion?: string;
  turn: number;
  [key: string]: unknown;
}

// ─── Trilemma ────────────────────────────────────────────────────────────────
export interface TrilemmaState {
  current_horn: string | null;
  horns_visited: string[];
  horns_escaped: string[];
  is_resolved: boolean;
  depth?: number;
  [key: string]: unknown;
}

export interface HornDetection {
  horn: string;
  confidence: number;
  evidence: string;
  explanation?: string;
}

export interface StanceDetection {
  stance: string;
  confidence: number;
  evidence: string;
}

// ─── Assessment ──────────────────────────────────────────────────────────────
export interface AssessmentQuestion {
  id: string;
  text: string;
  options: { key: string; text: string; stance_signal: string }[];
}

export interface AssessmentResult {
  scores: Record<string, number>;
  recommended_actors: number[];
  timestamp: string;
  [key: string]: unknown;
}

// ─── Gamification ────────────────────────────────────────────────────────────
export interface Achievement {
  id: string;
  title?: string;
  name?: string;
  description?: string;
  xp_reward?: number;
  unlocked_at?: string;
  [key: string]: unknown;
}

export interface GamificationProfile {
  xp: number;
  level: number;
  xp_progress: number;
  xp_needed: number;
  achievements: Achievement[];
}

export interface ProficiencyProfile {
  awareness: number;
  quality: number;
  flexibility: number;
  composure: number | null;
}

export interface GrowthReport {
  session_scores?: { session_id: number; score: number }[];
  score_trend?: { session_id: number; score: number; date: string }[];
  improvement?: number;
  stance_journey?: string[];
  [key: string]: unknown;
}

export interface Milestone {
  id: string;
  name: string;
  description: string;
  category?: string;
  icon?: string;
  xp_reward: number;
  unlocked: boolean;
  unlocked_at?: string;
}

// ─── Analytics ───────────────────────────────────────────────────────────────
export interface SessionAnalysis {
  analysis: Record<string, unknown>;
  score: Record<string, unknown>;
}

export interface SessionScore {
  total: number;
  grade: string;
  dimensions: Record<string, number>;
}

// ─── WebSocket Messages ──────────────────────────────────────────────────────
export type WSClientMessage =
  | { type: 'message'; content: string }
  | { type: 'end_session' }
  | { type: 'end_utterance' }
  | { type: 'end_debrief' };

export type WSServerMessage =
  | { type: 'stream_start' }
  | { type: 'stream_delta'; content: string }
  | { type: 'stream_end' }
  | { type: 'trilemma_update'; state: TrilemmaState; horn_detection?: HornDetection }
  | { type: 'stance_update'; detection: StanceDetection }
  | { type: 'coaching'; annotation: CoachingAnnotation }
  | { type: 'session_ended'; outcome: Record<string, unknown> }
  | { type: 'state_change'; state: 'listening' | 'processing' | 'speaking' }
  | { type: 'barge_in' }
  | { type: 'transcription'; text: string }
  | { type: 'vocal_state'; composure_score: number; [key: string]: unknown }
  | { type: 'audio_end' }
  | { type: 'latency_report'; turn: number; stt_ms: number; llm_ms: number; tts_first_byte_ms: number; total_ms: number }
  | { type: 'pong'; server_ts: number; client_ts?: number }
  | { type: 'debrief_start'; session_id: number }
  | { type: 'error'; detail: string };
