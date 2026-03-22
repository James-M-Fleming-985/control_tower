import { useMilestones, useGamificationProfile } from '@/hooks/use-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { Trophy, Lock, CheckCircle } from 'lucide-react';

export function AchievementsPage() {
  const { data: profile } = useGamificationProfile();
  const { data, isLoading } = useMilestones();

  const milestones = data?.milestones ?? [];
  const unlockedCount = milestones.filter((m) => m.unlocked).length;
  const total = milestones.length;

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Achievements</h1>
        <p className="text-sm text-muted-foreground">
          {unlockedCount} of {total} milestones unlocked
        </p>
      </div>

      <Progress value={total > 0 ? (unlockedCount / total) * 100 : 0} className="h-2 max-w-md" />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {milestones.map((m) => (
          <Card key={m.id} className={m.unlocked ? 'border-primary/50' : 'opacity-60'}>
            <CardContent className="pt-5 space-y-2">
              <div className="flex items-center gap-2">
                {m.unlocked ? (
                  <CheckCircle className="h-5 w-5 text-primary shrink-0" />
                ) : (
                  <Lock className="h-5 w-5 text-muted-foreground shrink-0" />
                )}
                <h3 className="font-semibold text-sm">{m.name}</h3>
              </div>
              <p className="text-xs text-muted-foreground">{m.description}</p>
              {m.category && (
                <Badge variant="outline" className="text-[10px]">{m.category}</Badge>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Inline achievements list */}
      {profile?.achievements && (profile.achievements as unknown[]).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Trophy className="h-4 w-4 text-primary" /> Earned Achievements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {(profile.achievements as Array<{ id: string; title?: string; name?: string }>).map((a) => (
                <Badge key={a.id}>{a.title ?? a.name ?? a.id}</Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
