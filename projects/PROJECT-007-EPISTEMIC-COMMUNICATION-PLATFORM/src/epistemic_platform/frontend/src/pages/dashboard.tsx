import { useNavigate } from 'react-router-dom';
import { useGamificationProfile, useProficiency, useGrowth, useSessions } from '@/hooks/use-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { xpProgress } from '@/lib/utils';
import { LEVEL_NAMES } from '@/lib/constants';
import { BarChart3, Zap, Target, TrendingUp, ArrowRight, BookOpen, MessageSquare, CheckCircle2 } from 'lucide-react';
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

const PROFICIENCY_LABELS: Record<string, string> = {
  awareness: 'Awareness',
  quality: 'Quality',
  flexibility: 'Flexibility',
  composure: 'Composure',
  overall: 'Overall',
  gricean: 'Gricean Clarity',
  trilemma: 'Trilemma Navigation',
  engagement: 'Engagement Depth',
};

const AXIS_TIPS: Record<string, string> = {
  awareness: 'Practice noticing your own assumptions. Before responding, ask yourself: "What am I taking for granted here?" Try paraphrasing the other person\'s view before giving your own.',
  quality: 'Focus on supporting your claims with reasons. Instead of stating opinions, explain *why* you hold them and invite the other person to challenge your reasoning.',
  flexibility: 'When you disagree, try steelmanning — restate the strongest version of the other person\'s argument before responding. Look for partial truths in opposing views.',
  composure: 'You\'re doing well staying calm under pressure. To go further, practise sitting with discomfort when your beliefs are challenged instead of deflecting.',
  overall: 'Keep practising across all dimensions. Aim for balanced growth rather than focusing on a single skill.',
};

const JOURNEY_STAGES = [
  { level: 0, label: 'Assessment', icon: BookOpen },
  { level: 1, label: 'Beginner', icon: MessageSquare },
  { level: 3, label: 'Intermediate', icon: Target },
  { level: 5, label: 'Advanced', icon: TrendingUp },
  { level: 8, label: 'Expert', icon: Zap },
];

export function DashboardPage() {
  const navigate = useNavigate();
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
        .map(([k, v]) => {
          // v may be {name, value, history} object or a plain number (overall)
          const raw = typeof v === 'object' && v !== null && 'value' in (v as Record<string, unknown>)
            ? (v as { value: number }).value
            : Number(v ?? 0);
          return { axis: PROFICIENCY_LABELS[k] ?? k.replace(/_/g, ' '), key: k, value: Math.round(raw * 100) };
        })
    : [];

  // Growth line data
  const growthData = growth?.score_trend
    ? (growth.score_trend as Array<{ session_id: number; value: number }>).map((s, i) => ({
        session: i + 1,
        score: Math.round(s.value * 10) / 10,
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

      {/* Learning Path */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Your Learning Journey</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-1 overflow-x-auto pb-2">
            {JOURNEY_STAGES.map((stage, i) => {
              const reached = level >= stage.level || (stage.level === 0 && (sessions?.length ?? 0) >= 0);
              const current = i < JOURNEY_STAGES.length - 1
                ? level >= stage.level && level < JOURNEY_STAGES[i + 1].level
                : level >= stage.level;
              const Icon = stage.icon;
              return (
                <div key={stage.label} className="flex items-center">
                  <div className={`flex flex-col items-center gap-1 px-3 py-2 rounded-md min-w-[80px] ${
                    current ? 'bg-primary/20 ring-1 ring-primary' : reached ? 'opacity-100' : 'opacity-40'
                  }`}>
                    {reached ? (
                      <CheckCircle2 className={`h-5 w-5 ${current ? 'text-primary' : 'text-green-400'}`} />
                    ) : (
                      <Icon className="h-5 w-5 text-muted-foreground" />
                    )}
                    <span className={`text-xs font-medium ${current ? 'text-primary' : ''}`}>{stage.label}</span>
                    {stage.level > 0 && <span className="text-[10px] text-muted-foreground">L{stage.level}+</span>}
                  </div>
                  {i < JOURNEY_STAGES.length - 1 && (
                    <ArrowRight className={`h-4 w-4 mx-1 ${reached ? 'text-primary' : 'text-muted-foreground/30'}`} />
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Charts row */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Proficiency Radar */}
        {radarData.length > 0 ? (
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
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Proficiency Radar</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center py-8 text-center">
              <Target className="h-10 w-10 text-muted-foreground/40 mb-3" />
              <p className="text-sm text-muted-foreground">Complete your first conversation to see your proficiency radar</p>
              <Button variant="outline" size="sm" className="mt-3" onClick={() => navigate('/actors')}>
                Start a conversation <ArrowRight className="ml-1 h-3 w-3" />
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Growth chart */}
        {growthData.length > 1 ? (
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
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <TrendingUp className="h-4 w-4" /> Score Growth
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center py-8 text-center">
              <BarChart3 className="h-10 w-10 text-muted-foreground/40 mb-3" />
              <p className="text-sm text-muted-foreground">
                {growthData.length === 1
                  ? 'One more session will show your growth trend'
                  : 'Complete conversations to track your score over time'}
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Strengths / Weaknesses + Recommended Next */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Strengths & Weaknesses */}
        {radarData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Strengths &amp; Areas to Improve</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[...radarData].sort((a, b) => b.value - a.value).map((d, i) => {
                const isStrength = i < 2 && d.value >= 40;
                const isWeakness = i >= radarData.length - 1 || d.value < 30;
                return (
                  <div key={d.axis} className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">{d.axis}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">{d.value}%</span>
                        {isStrength && <Badge variant="default" className="text-[10px] px-1.5 py-0">Strength</Badge>}
                        {isWeakness && <Badge variant="outline" className="text-[10px] px-1.5 py-0 border-amber-500/50 text-amber-400">Improve</Badge>}
                      </div>
                    </div>
                    <Progress value={d.value} className="h-1.5" />
                  </div>
                );
              })}
            </CardContent>
          </Card>
        )}

        {/* Recommended Next */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recommended Next</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {(sessions?.length ?? 0) === 0 ? (
              <>
                <p className="text-sm text-muted-foreground">Start your first practice conversation to get personalised recommendations.</p>
                <Button size="sm" onClick={() => navigate('/actors')}>
                  Choose an actor <ArrowRight className="ml-1 h-3 w-3" />
                </Button>
              </>
            ) : (
              <>
                {radarData.length > 0 && (() => {
                  const weakest = [...radarData].sort((a, b) => a.value - b.value)[0];
                  const axisKey = weakest.key;
                  const label = PROFICIENCY_LABELS[axisKey] ?? weakest.axis;
                  const tip = AXIS_TIPS[axisKey] ?? 'Try a conversation that specifically challenges this skill.';
                  return (
                    <div className="rounded-md border border-card-border p-3 space-y-1">
                      <p className="text-sm font-medium">Focus on: {label} ({weakest.value}%)</p>
                      <p className="text-xs text-muted-foreground">{tip}</p>
                    </div>
                  );
                })()}
                <div className="rounded-md border border-card-border p-3 space-y-1">
                  <p className="text-sm font-medium">Try a new scenario</p>
                  <p className="text-xs text-muted-foreground">Guided scenarios push you to practice specific epistemological skills.</p>
                  <Button variant="outline" size="sm" className="mt-1" onClick={() => navigate('/scenarios')}>
                    Browse scenarios <ArrowRight className="ml-1 h-3 w-3" />
                  </Button>
                </div>
                {(sessions?.length ?? 0) >= 3 && level < 3 && (
                  <div className="rounded-md border border-card-border p-3 space-y-1">
                    <p className="text-sm font-medium">Review past debriefs</p>
                    <p className="text-xs text-muted-foreground">Your coach debrief offers personalised analysis — revisit previous sessions for deeper insight.</p>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
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
