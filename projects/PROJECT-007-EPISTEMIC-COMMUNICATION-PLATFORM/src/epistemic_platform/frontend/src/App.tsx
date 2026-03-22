import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from '@/components/layout/layout';
import { LoginPage } from '@/pages/login';
import { RegisterPage } from '@/pages/register';
import { AssessmentPage } from '@/pages/assessment';
import { ActorsPage } from '@/pages/actors';
import { ActorDetailPage } from '@/pages/actor-detail';
import { ScenariosPage } from '@/pages/scenarios';
import { ConversationPage } from '@/pages/conversation';
import { ResultsPage } from '@/pages/results';
import { DebriefPage } from '@/pages/debrief';
import { DashboardPage } from '@/pages/dashboard';
import { AchievementsPage } from '@/pages/achievements';
import { SettingsPage } from '@/pages/settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Authenticated */}
          <Route element={<Layout />}>
            <Route path="/assessment" element={<AssessmentPage />} />
            <Route path="/actors" element={<ActorsPage />} />
            <Route path="/actors/:id" element={<ActorDetailPage />} />
            <Route path="/scenarios" element={<ScenariosPage />} />
            <Route path="/conversation/:sessionId" element={<ConversationPage />} />
            <Route path="/results/:sessionId" element={<ResultsPage />} />
            <Route path="/debrief/:sessionId" element={<DebriefPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/achievements" element={<AchievementsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
