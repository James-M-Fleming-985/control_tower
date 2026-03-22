import { useAuthStore } from '@/stores/auth-store';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { xpProgress } from '@/lib/utils';
import { LEVEL_NAMES } from '@/lib/constants';

export function Header() {
  const user = useAuthStore((s) => s.user);
  if (!user) return null;

  const progress = xpProgress(user.xp, user.level);
  const levelName = LEVEL_NAMES[user.level] ?? `Level ${user.level}`;

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-card px-4 md:px-6">
      <div className="flex items-center gap-4 flex-1 min-w-0">
        {/* Level + XP bar */}
        <Badge variant="default" className="shrink-0">
          Lv.{user.level} {levelName}
        </Badge>
        <div className="hidden sm:flex items-center gap-2 flex-1 max-w-xs">
          <Progress value={progress} className="h-1.5" />
          <span className="text-xs text-muted-foreground whitespace-nowrap">
            {user.xp} XP
          </span>
        </div>
      </div>

      {/* User */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-muted-foreground hidden md:block">{user.display_name}</span>
        <div className="h-8 w-8 rounded-full bg-primary/30 flex items-center justify-center text-xs font-bold text-primary-foreground">
          {user.display_name.charAt(0).toUpperCase()}
        </div>
      </div>
    </header>
  );
}
