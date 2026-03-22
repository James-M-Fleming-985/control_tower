import { useGamificationProfile, useProficiency, useGrowth, useSessions } from '@/hooks/use-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { xpProgress } from '@/lib/utils';
import { LEVEL_NAMES } from '@/lib/constants';
import { BarChart3, Zap, Target, TrendingUp } from 'lucide-react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export function DashboardPage() {
  const { data: profile, isLoading: profileLoading } = useGamificationProfile();
  const { data: proficiency, isLoading: profLoading } = useProficiency();
  const { data: growth, isLoading: growthLoading } = useGrowth();
  const { data: sessions } = useSessions();

  const loading = profileLoading || profLoading || growthLoading;

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  // Proficiency radar data
  const radarData = proficiency
    ? Object.entries(proficiency)
        .filter(([k]) => !k.startsWith('_'))
        .map(([k, v]) => ({ axis: k.replace(/_/g, ' '), value: Math.round(Number(v ?? 0) * 100) }))
    : [];

  // Growth line data
  const growthData = growth?.session_scores
    ? (growth.session_scores as Array<{ session_id: number; score: number }>).map((s, i) => ({
        session: i + 1,
        score: s.score,
      }))
    : [];

  const level = profile?.level ?? 1;
  const levelName = LEVEL_NAMES[level] ?? `Level ${level}`;
  const xp = profile?.xp ?? 0;
  const progress = profile ? xpProgress(xp, level) : 0;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* Stats row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-5 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/20">
              <Zap className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Level</p>
              <p className="text-lg font-bold">{level} — {levelName}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5 space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">XP Progress</p>
              <span className="text-xs font-medium">{xp} XP</span>
            </div>
            <Progress value={progress} className="h-2" />
            {profile?.xp_needed && (
              <p className="text-[10px] text-muted-foreground">{profile.xp_progress}/{profile.xp_needed} to next level</p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/20">
              <Target className="h-5 w-5 text-green-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Sessions</p>
              <p className="text-lg font-bold">{sessions?.length ?? 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-500/20">
              <BarChart3 className="h-5 w-5 text-amber-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Achievements</p>
              <p className="text-lg font-bold">{profile?.achievements?.length ?? 0}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts row */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Proficiency Radar */}
        {radarData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Proficiency Radar</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={260}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#3b3b3b" />
                  <PolarAngleAxis dataKey="axis" tick={{ fill: '#a0a0a0', fontSize: 11 }} />
                  <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar dataKey="value" stroke="#6264A7" fill="#6264A7" fillOpacity={0.3} />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Growth chart */}
        {growthData.length > 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <TrendingUp className="h-4 w-4" /> Score Growth
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={growthData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#3b3b3b" />
                  <XAxis dataKey="session" tick={{ fill: '#a0a0a0', fontSize: 11 }} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#a0a0a0', fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#2d2d2d', border: '1px solid #3b3b3b', borderRadius: 8 }}
                    labelStyle={{ color: '#a0a0a0' }}
                  />
                  <Line type="monotone" dataKey="score" stroke="#6264A7" strokeWidth={2} dot={{ fill: '#6264A7', r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Recent achievements */}
      {profile?.achievements && profile.achievements.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Achievements</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {(profile.achievements as Array<{ id: string; title?: string; name?: string }>)
                .slice(-8)
                .map((a) => (
                  <Badge key={a.id} variant="default" className="text-xs">
                    🏆 {a.title ?? a.name ?? a.id}
                  </Badge>
                ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
