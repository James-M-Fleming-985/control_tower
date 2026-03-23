import { Navigate, Outlet } from 'react-router-dom';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { useAuthStore } from '@/stores/auth-store';

export function Layout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;

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
