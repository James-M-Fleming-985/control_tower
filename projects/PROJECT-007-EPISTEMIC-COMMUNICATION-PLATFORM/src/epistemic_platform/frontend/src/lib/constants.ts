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
  2: 'Practitioner',
  3: 'Communicator',
  4: 'Advanced Thinker',
  5: 'Expert',
};

export const LEVEL_DESCRIPTIONS: Record<number, string> = {
  1: 'Demonstrate basic understanding across beginner scenarios with all perspectives.',
  2: 'Develop stronger arguments across beginner and intermediate scenarios.',
  3: 'Show competent reasoning and communication across intermediate scenarios.',
  4: 'Demonstrate sophisticated argumentation across advanced scenarios.',
  5: 'Master advanced reasoning and meta-epistemology at the expert level.',
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
