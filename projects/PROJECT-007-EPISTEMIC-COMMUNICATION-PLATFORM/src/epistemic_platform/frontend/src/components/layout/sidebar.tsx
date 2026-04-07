import { NavLink } from 'react-router-dom';
import {
  MessageSquare,
  Users,
  Map,
  BarChart3,
  Trophy,
  Settings,
  LogOut,
  History,
  FlaskConical,
} from 'lucide-react';
import { useAuth } from '@/hooks/use-auth';
import { useAuthStore } from '@/stores/auth-store';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { to: '/actors', label: 'Actors', icon: Users },
  { to: '/scenarios', label: 'Scenarios', icon: Map },
  { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
  { to: '/sessions', label: 'History', icon: History },
  { to: '/achievements', label: 'Achievements', icon: Trophy },
  { to: '/settings', label: 'Settings', icon: Settings },
];

const ADMIN_NAV_ITEMS = [
  { to: '/admin/avatar-lab', label: 'Avatar Lab', icon: FlaskConical },
];

export function Sidebar() {
  const { handleLogout } = useAuth();
  const user = useAuthStore((s) => s.user);
  const isAdmin = user?.role === 'admin';

  return (
    <aside className="flex h-full w-16 flex-col items-center border-r border-sidebar-border bg-sidebar py-4 md:w-56">
      {/* Logo */}
      <div className="mb-8 flex items-center gap-2 px-3">
        <MessageSquare className="h-6 w-6 text-primary" />
        <span className="hidden text-sm font-semibold text-foreground md:block">Epistemic</span>
      </div>

      {/* Nav links */}
      <nav className="flex flex-1 flex-col gap-1 px-2 w-full">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-sm px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-active text-foreground'
                  : 'text-sidebar-foreground hover:bg-sidebar-active/50 hover:text-foreground',
              )
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            <span className="hidden md:block">{item.label}</span>
          </NavLink>
        ))}

        {/* Admin section */}
        {isAdmin && (
          <>
            <div className="my-2 border-t border-sidebar-border" />
            <span className="px-3 py-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground hidden md:block">
              Admin
            </span>
            {ADMIN_NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-sm px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-sidebar-active text-foreground'
                      : 'text-sidebar-foreground hover:bg-sidebar-active/50 hover:text-foreground',
                  )
                }
              >
                <item.icon className="h-5 w-5 shrink-0" />
                <span className="hidden md:block">{item.label}</span>
              </NavLink>
            ))}
          </>
        )}
      </nav>

      {/* Logout */}
      <button
        onClick={handleLogout}
        className="flex items-center gap-3 px-3 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors w-full mx-2"
      >
        <LogOut className="h-5 w-5 shrink-0" />
        <span className="hidden md:block">Sign out</span>
      </button>
    </aside>
  );
}
