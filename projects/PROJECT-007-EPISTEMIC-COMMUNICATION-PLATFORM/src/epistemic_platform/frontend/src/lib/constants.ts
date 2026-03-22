export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  ASSESSMENT: '/assessment',
  ACTORS: '/actors',
  ACTOR_DETAIL: '/actors/:id',
  SCENARIOS: '/scenarios',
  CONVERSATION: '/conversation/:id',
  SESSION_RESULTS: '/sessions/:id/results',
  DEBRIEF: '/sessions/:id/debrief',
  DASHBOARD: '/dashboard',
  SETTINGS: '/settings',
} as const;

export const LEVEL_NAMES: Record<number, string> = {
  1: 'Explorer',
  2: 'Horn Spotter',
  3: 'Escape Artist',
  4: 'Stance Surfer',
  5: 'Maxim Keeper',
  6: 'Multi-Actor',
  7: 'Trilemma Navigator',
  8: "Devil's Advocate",
  9: 'Epistemic Athlete',
  10: 'Philosopher',
};

export const HORN_COLORS: Record<string, string> = {
  regress: '#ef4444',
  circularity: '#f59e0b',
  dogmatism: '#8b5cf6',
  escaped: '#66bb6a',
  exploring: '#6264A7',
};

export const STANCE_COLORS: Record<string, string> = {
  foundationalist: '#ef4444',
  coherentist: '#3b82f6',
  pragmatist: '#f59e0b',
  skeptic: '#8b5cf6',
  empiricist: '#10b981',
  relativist: '#ec4899',
  infinitist: '#6366f1',
  foundherentist: '#14b8a6',
  virtue_epistemologist: '#f97316',
  fallibilist: '#64748b',
};
