import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGamificationProfile, useProficiency, useGrowth, useSessions } from '@/hooks/use-api';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { xpProgress } from '@/lib/utils';
import { LEVEL_NAMES } from '@/lib/constants';
import { BarChart3, Zap, Target, TrendingUp, ArrowRight, BookOpen, MessageSquare, CheckCircle2, Eye } from 'lucide-react';
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
  Tooltip as RechartsTooltip,
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
  { level: 0, label: 'Assessment', icon: BookOpen, desc: 'Complete the epistemological assessment to identify your starting perspective.' },
  { level: 1, label: 'Beginner', icon: MessageSquare, desc: 'Practice basic conversations. Learn to recognise trilemma horns and Gricean maxims.' },
  { level: 3, label: 'Intermediate', icon: Target, desc: 'Engage with diverse scenarios. Start shifting between epistemological stances.' },
  { level: 5, label: 'Advanced', icon: TrendingUp, desc: 'Navigate complex dialogues. Demonstrate consistent flexibility and reasoned composure.' },
  { level: 8, label: 'Expert', icon: Zap, desc: 'Master all dimensions. Fluently adopt and critique multiple epistemological perspectives.' },
];

const SCORE_GRADE = (v: number) => v >= 95 ? 'S' : v >= 80 ? 'A' : v >= 65 ? 'B' : v >= 50 ? 'C' : 'D';

const STANCE_COLORS: Record<string, string> = {
  foundationalist: '#ef4444',
  coherentist: '#3b82f6',
  pragmatist: '#f59e0b',
  skeptic: '#8b5cf6',
  empiricist: '#10b981',
  relativist: '#ec4899',
  infinitist: '#6366f1',
  foundherentist: '#14b8a6',
  'virtue epistemologist': '#f97316',
  fallibilist: '#64748b',
};

const STANCE_DESCRIPTIONS: Record<string, string> = {
  foundationalist: 'You ground knowledge in indubitable foundational truths — basic beliefs that don\'t need further justification.',
  coherentist: 'You evaluate beliefs by how well they fit together — truth is about coherence within your belief system.',
  pragmatist: 'You measure ideas by their practical outcomes — what works in practice is what counts as true.',
  skeptic: 'You question claims to knowledge systematically — healthy doubt drives you to examine evidence closely.',
  empiricist: 'You privilege experience and observation — knowledge comes from what can be seen, tested, and measured.',
  relativist: 'You recognise that truth can be framework-dependent — context and perspective shape what counts as knowledge.',
  infinitist: 'You accept that justification chains can extend indefinitely — every reason can itself be questioned.',
  foundherentist: 'You blend foundational experience with coherence — a hybrid approach combining the best of both.',
  'virtue epistemologist': 'You link knowledge to intellectual character — curiosity, open-mindedness, and rigour lead to truth.',
  fallibilist: 'You hold that all beliefs are revisable — being willing to change your mind is an epistemic strength.',
};

const GROWTH_DIMENSIONS = [
  { key: 'score', label: 'Overall Score', color: '#6264A7', desc: 'Weighted composite of all dimensions below, adjusted by session difficulty.' },
  { key: 'gricean', label: 'Gricean Quality', color: '#3b82f6', desc: 'How well you follow conversational maxims: be clear, truthful, relevant, and concise.' },
  { key: 'trilemma', label: 'Trilemma Navigation', color: '#ef4444', desc: 'Your ability to recognise and escape Münchhausen trilemma horns (circular, regressive, dogmatic).' },
  { key: 'flexibility', label: 'Stance Flexibility', color: '#10b981', desc: 'How many different epistemological perspectives you demonstrate in a single session.' },
  { key: 'composure', label: 'Composure', color: '#f59e0b', desc: 'Emotional steadiness during voice conversations when your views are challenged.' },
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

  // Growth line data — merge all dimension trends by session index
  const growthData = (() => {
    const scoreTrend = (growth?.score_trend ?? []) as Array<{ session_id: number; value: number }>;
    const griceanTrend = (growth?.gricean_trend ?? []) as Array<{ session_id: number; value: number }>;
    const trilemmaTrend = (growth?.trilemma_trend ?? []) as Array<{ session_id: number; value: number }>;
    const flexTrend = (growth?.flexibility_trend ?? []) as Array<{ session_id: number; value: number }>;
    const compTrend = (growth?.composure_trend ?? []) as Array<{ session_id: number; value: number }>;
    if (!scoreTrend.length) return [];
    return scoreTrend.map((s, i) => ({
      session: `Session ${i + 1}`,
      score: Math.round(s.value * 10) / 10,
      gricean: Math.round((griceanTrend[i]?.value ?? 0) * 10) / 10,
      trilemma: Math.round((trilemmaTrend[i]?.value ?? 0) * 10) / 10,
      flexibility: Math.round((flexTrend[i]?.value ?? 0) * 10) / 10,
      composure: compTrend.length > 0 ? Math.round((compTrend[i]?.value ?? 0) * 10) / 10 : undefined,
    }));
  })();

  const stancesEncountered = (growth?.all_stances_encountered ?? []) as string[];

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
          <CardDescription className="text-xs">Progress through stages by completing conversations and earning XP</CardDescription>
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
                <div key={stage.label} className="flex items-center group">
                  <div className={`relative flex flex-col items-center gap-1 px-3 py-2 rounded-md min-w-[80px] ${
                    current ? 'bg-primary/20 ring-1 ring-primary' : reached ? 'opacity-100' : 'opacity-40'
                  }`}>
                    {reached ? (
                      <CheckCircle2 className={`h-5 w-5 ${current ? 'text-primary' : 'text-green-400'}`} />
                    ) : (
                      <Icon className="h-5 w-5 text-muted-foreground" />
                    )}
                    <span className={`text-xs font-medium ${current ? 'text-primary' : ''}`}>{stage.label}</span>
                    {stage.level > 0 && <span className="text-[10px] text-muted-foreground">L{stage.level}+</span>}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 rounded-md bg-popover p-2 text-[10px] text-popover-foreground shadow-md opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-10 border">
                      {stage.desc}
                    </div>
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
          <ScoreGrowthChart data={growthData} hasComposure={!!growth?.composure_trend && (growth.composure_trend as unknown[]).length > 0} />
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

      {/* Perspective Evolution */}
      {stancesEncountered.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Eye className="h-4 w-4" /> Your Epistemological Perspectives
            </CardTitle>
            <CardDescription className="text-xs">
              Stances detected across your conversations — as you practise, you&apos;ll explore more perspectives and become more epistemologically well-rounded.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {stancesEncountered.map((stance) => (
                <Badge
                  key={stance}
                  variant="outline"
                  className="text-xs px-2 py-1 border-2"
                  style={{ borderColor: STANCE_COLORS[stance] ?? '#666', color: STANCE_COLORS[stance] ?? '#aaa' }}
                >
                  {stance.charAt(0).toUpperCase() + stance.slice(1)}
                </Badge>
              ))}
              {stancesEncountered.length < 4 && (
                <Badge variant="outline" className="text-xs px-2 py-1 opacity-40 border-dashed">
                  + {10 - stancesEncountered.length} more to discover
                </Badge>
              )}
            </div>
            <div className="space-y-2">
              {stancesEncountered.map((stance) => (
                <div key={stance} className="rounded-md border p-2.5 space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: STANCE_COLORS[stance] ?? '#666' }} />
                    <span className="text-sm font-medium">{stance.charAt(0).toUpperCase() + stance.slice(1)}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">{STANCE_DESCRIPTIONS[stance] ?? 'A unique epistemological perspective.'}</p>
                </div>
              ))}
            </div>
            {stancesEncountered.length < 3 && (
              <p className="text-xs text-muted-foreground italic">
                Tip: Try taking a different position in your next conversation. Deliberately argue from a perspective you wouldn&apos;t normally adopt.
              </p>
            )}
          </CardContent>
        </Card>
      )}

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

/* ── Score Growth Chart with dimension toggle ── */
function ScoreGrowthChart({ data, hasComposure }: { data: Array<Record<string, unknown>>; hasComposure: boolean }) {
  const [visibleLines, setVisibleLines] = useState<Set<string>>(new Set(['score']));

  const toggle = (key: string) => {
    setVisibleLines((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        if (next.size > 1) next.delete(key); // keep at least one
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const dims = hasComposure ? GROWTH_DIMENSIONS : GROWTH_DIMENSIONS.filter((d) => d.key !== 'composure');

  // Custom tooltip
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    const score = payload.find((p: { dataKey: string }) => p.dataKey === 'score')?.value ?? 0;
    return (
      <div className="rounded-md bg-popover border p-2 text-xs shadow-md min-w-[140px]">
        <p className="font-medium text-popover-foreground mb-1">{label} — Grade {SCORE_GRADE(score)}</p>
        {payload.map((entry: { dataKey: string; value: number; color: string }) => (
          <div key={entry.dataKey} className="flex items-center justify-between gap-3">
            <span style={{ color: entry.color }}>{dims.find((d) => d.key === entry.dataKey)?.label ?? entry.dataKey}</span>
            <span className="text-popover-foreground font-medium">{entry.value}%</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <TrendingUp className="h-4 w-4" /> Score Growth
        </CardTitle>
        <CardDescription className="text-xs">
          Your session performance over time. Each session is scored 0–100 across multiple dimensions, then graded S/A/B/C/D.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap gap-1.5">
          {dims.map((d) => (
            <button
              key={d.key}
              onClick={() => toggle(d.key)}
              className={`text-[10px] px-2 py-0.5 rounded-full border transition-all ${
                visibleLines.has(d.key)
                  ? 'opacity-100 font-medium'
                  : 'opacity-40 hover:opacity-70'
              }`}
              style={{
                borderColor: d.color,
                color: visibleLines.has(d.key) ? d.color : undefined,
                backgroundColor: visibleLines.has(d.key) ? `${d.color}15` : undefined,
              }}
              title={d.desc}
            >
              {d.label}
            </button>
          ))}
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3b3b3b" />
            <XAxis dataKey="session" tick={{ fill: '#a0a0a0', fontSize: 10 }} />
            <YAxis domain={[0, 100]} tick={{ fill: '#a0a0a0', fontSize: 10 }} label={{ value: 'Score %', angle: -90, position: 'insideLeft', fill: '#666', fontSize: 10 }} />
            <RechartsTooltip content={<CustomTooltip />} />
            {dims.map((d) =>
              visibleLines.has(d.key) ? (
                <Line
                  key={d.key}
                  type="monotone"
                  dataKey={d.key}
                  stroke={d.color}
                  strokeWidth={d.key === 'score' ? 2.5 : 1.5}
                  dot={{ fill: d.color, r: d.key === 'score' ? 3 : 2 }}
                  strokeDasharray={d.key === 'score' ? undefined : '4 2'}
                />
              ) : null,
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
