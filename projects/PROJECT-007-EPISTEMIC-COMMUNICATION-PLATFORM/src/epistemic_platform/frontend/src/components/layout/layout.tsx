import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { useAuthStore } from '@/stores/auth-store';

export function Layout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const user = useAuthStore((s) => s.user);
  const location = useLocation();

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  // Soft-gate: redirect to assessment if user hasn't completed it yet
  if (
    user &&
    (!user.assessment_history || user.assessment_history.length === 0) &&
    location.pathname !== '/assessment'
  ) {
    return <Navigate to="/assessment" replace />;
  }

  return (
    <div className="flex h-screen bg-background text-foreground">
      <Sidebar />
      <div className="flex flex-1 flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-auto p-4 md:p-6">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  );
}
