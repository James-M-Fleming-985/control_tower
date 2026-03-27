import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGamificationProfile, useProficiency, useGrowth, useSessions, useUpdateProfile, useSyllabus, useActors } from '@/hooks/use-api';
import { useAuthStore } from '@/stores/auth-store';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { LEVEL_NAMES, LEVEL_DESCRIPTIONS } from '@/lib/constants';
import { BarChart3, Zap, Target, TrendingUp, ArrowRight, CheckCircle2, Eye, Crosshair } from 'lucide-react';
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
  ReferenceLine,
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

/* Unified dimension colour palette — used by radar, growth chart, strengths, tooltips */
const DIMENSION_COLORS: Record<string, string> = {
  awareness: '#3b82f6',   // blue
  quality: '#6264A7',     // indigo (brand)
  flexibility: '#10b981', // green
  composure: '#f59e0b',   // amber
  overall: '#8b5cf6',     // violet
  gricean: '#3b82f6',     // alias → awareness
  trilemma: '#ef4444',    // red
  engagement: '#ec4899',  // pink
};

const SYLLABUS_LEVELS = [
  { level: 1, label: 'Explorer', min: 'C' },
  { level: 2, label: 'Practitioner', min: 'C+' },
  { level: 3, label: 'Communicator', min: 'B' },
  { level: 4, label: 'Advanced Thinker', min: 'B+' },
  { level: 5, label: 'Expert', min: 'A' },
];

const SCORE_GRADE = (v: number) => v >= 95 ? 'S' : v >= 80 ? 'A' : v >= 65 ? 'B' : v >= 50 ? 'C' : 'D';

const GRADE_INFO: Record<string, { label: string; desc: string; tip: string }> = {
  S: { label: 'S — Superb', desc: '≥95% — Exceptional mastery across all dimensions.', tip: 'You\'re performing at the highest level. Keep challenging yourself with harder scenarios.' },
  A: { label: 'A — Advanced', desc: '80–94% — Strong, well-rounded performance.', tip: 'Excellent work. Polish your weakest dimension to push into S territory.' },
  B: { label: 'B — Building', desc: '65–79% — Solid skills with room to grow.', tip: 'You\'re on a good trajectory. Focus on consistency across sessions.' },
  C: { label: 'C — Capable', desc: '50–64% — Developing core abilities.', tip: 'You\'re getting the basics. Try to pause and reflect before responding in conversations.' },
  D: { label: 'D — Developing', desc: 'Below 50% — Early stage of learning.', tip: 'Everyone starts here. Each conversation builds your skills — keep practising and review your debriefs.' },
};

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
  const { data: syllabus } = useSyllabus();
  const { data: actors } = useActors();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const updateProfile = useUpdateProfile();

  // User targets from preferences
  const userTargets = (user?.preferences?.targets ?? {}) as Record<string, number>;
  const [editingTargets, setEditingTargets] = useState(false);
  const [draftTargets, setDraftTargets] = useState<Record<string, number>>({});

  const openTargetEditor = useCallback(() => {
    setDraftTargets({ ...userTargets });
    setEditingTargets(true);
  }, [userTargets]);

  const saveTargets = useCallback(() => {
    const newPrefs = { ...(user?.preferences ?? {}), targets: draftTargets };
    updateProfile.mutate({ preferences: newPrefs }, {
      onSuccess: (updated) => {
        updateUser({ preferences: updated.preferences });
        setEditingTargets(false);
      },
    });
  }, [draftTargets, user?.preferences, updateProfile, updateUser]);

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

  // Actor ID → name lookup for syllabus grid
  const actorMap = new Map<string, string>();
  actors?.forEach((a) => actorMap.set(String(a.id), a.name));

  // Collect all unique actor IDs from syllabus items for grid columns
  const syllabusActorIds: string[] = (() => {
    const ids = new Set<string>();
    syllabus?.items?.forEach((item) => {
      Object.keys(item.actors).forEach((id) => ids.add(id));
    });
    return Array.from(ids);
  })();

  // Proficiency radar data
  const radarData = proficiency
    ? Object.entries(proficiency)
        .filter(([k]) => !k.startsWith('_'))
        .map(([k, v]) => {
          // v may be {name, value, history} object or a plain number (overall)
          const raw = typeof v === 'object' && v !== null && 'value' in (v as Record<string, unknown>)
            ? (v as { value: number }).value
            : Number(v ?? 0);
          return { axis: PROFICIENCY_LABELS[k] ?? k.replace(/_/g, ' '), key: k, value: Math.round(raw * 100), target: userTargets[k] ?? undefined };
        })
    : [];

  const hasTargets = Object.keys(userTargets).length > 0;

  // Growth line data — merge all dimension trends by session_id (not index)
  // Composure only has data for voice sessions, so index-based mapping misaligns
  const growthData = (() => {
    const scoreTrend = (growth?.score_trend ?? []) as Array<{ session_id: number; value: number; timestamp?: string }>;
    const griceanTrend = (growth?.gricean_trend ?? []) as Array<{ session_id: number; value: number }>;
    const trilemmaTrend = (growth?.trilemma_trend ?? []) as Array<{ session_id: number; value: number }>;
    const flexTrend = (growth?.flexibility_trend ?? []) as Array<{ session_id: number; value: number }>;
    const compTrend = (growth?.composure_trend ?? []) as Array<{ session_id: number; value: number }>;
    if (!scoreTrend.length) return [];
    // Build lookup maps keyed by session_id for sparse dimensions
    const toMap = (arr: Array<{ session_id: number; value: number }>) =>
      new Map(arr.map((e) => [e.session_id, e.value]));
    const griceanMap = toMap(griceanTrend);
    const trilemmaMap = toMap(trilemmaTrend);
    const flexMap = toMap(flexTrend);
    const compMap = toMap(compTrend);
    return scoreTrend.map((s, i) => ({
      session: `Session ${i + 1}`,
      date: s.timestamp ? new Date(s.timestamp).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '',
      score: Math.round(s.value * 10) / 10,
      gricean: Math.round((griceanMap.get(s.session_id) ?? 0) * 10) / 10,
      trilemma: Math.round((trilemmaMap.get(s.session_id) ?? 0) * 10) / 10,
      flexibility: Math.round((flexMap.get(s.session_id) ?? 0) * 10) / 10,
      composure: compMap.has(s.session_id) ? Math.round((compMap.get(s.session_id)!) * 10) / 10 : undefined,
    }));
  })();

  const stancesEncountered = (growth?.all_stances_encountered ?? []) as string[];

  const level = syllabus?.current_level ?? profile?.level ?? 1;
  const levelName = LEVEL_NAMES[level] ?? `Level ${level}`;
  const syllabusCompleted = syllabus?.completed_completions ?? 0;
  const syllabusTotal = syllabus?.total_completions ?? 0;
  const syllabusPercentage = syllabus?.percentage ?? 0;

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
            <div className="group relative">
              <p className="text-xs text-muted-foreground">Level</p>
              <p className="text-lg font-bold">{level} — {levelName}</p>
              {LEVEL_DESCRIPTIONS[level] && (
                <div className="absolute top-full left-0 mt-1 w-56 rounded-md bg-popover p-2 text-[10px] text-popover-foreground shadow-md opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 border">
                  {LEVEL_DESCRIPTIONS[level]}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5 space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">Syllabus Progress</p>
              <span className="text-xs font-medium">{syllabusCompleted}/{syllabusTotal}</span>
            </div>
            <Progress value={syllabusPercentage} className="h-2" />
            <p className="text-[10px] text-muted-foreground">
              {syllabus?.has_syllabus
                ? `${Math.round(syllabusPercentage)}% — min grade ${syllabus?.min_grade ?? 'C'}`
                : 'Complete assessment to generate your syllabus'}
            </p>
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

      {/* Syllabus Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Syllabus Progress</CardTitle>
          <CardDescription className="text-xs">Complete every scenario with all 6 actors at the required grade to advance</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* ── Stepper bar (Salesforce-style pipeline) ── */}
          <div className="flex items-center">
            {SYLLABUS_LEVELS.map((sl, i) => {
              const reached = level > sl.level;
              const current = level === sl.level;
              return (
                <div key={sl.level} className="flex items-center flex-1 last:flex-none">
                  {/* Stage pill */}
                  <div className={`
                    relative flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium whitespace-nowrap border transition-all
                    ${reached
                      ? 'bg-green-500/15 border-green-500/40 text-green-400'
                      : current
                        ? 'bg-primary/15 border-primary/50 text-primary ring-2 ring-primary/20'
                        : 'bg-muted/50 border-border text-muted-foreground'
                    }
                  `}>
                    {reached ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-green-400" />
                    ) : current ? (
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
                      </span>
                    ) : (
                      <span className="h-2 w-2 rounded-full bg-muted-foreground/30" />
                    )}
                    <span>{sl.label}</span>
                    <span className="text-[9px] opacity-60">({sl.min})</span>
                  </div>
                  {/* Connector line */}
                  {i < SYLLABUS_LEVELS.length - 1 && (
                    <div className={`flex-1 h-px mx-1 ${reached ? 'bg-green-500/40' : 'bg-border'}`} />
                  )}
                </div>
              );
            })}
          </div>

          {/* Level summary */}
          {syllabus?.has_syllabus && (
            <p className="text-xs text-muted-foreground text-center">
              Level {level}: {levelName} — {syllabusCompleted} of {syllabusTotal} completions ({Math.round(syllabusPercentage)}%)
            </p>
          )}

          {/* ── Scenario × Actor grid table ── */}
          {syllabus?.has_syllabus && syllabus.items && syllabus.items.length > 0 ? (
            <div className="overflow-x-auto -mx-6 px-6">
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-2 pr-3 font-medium text-muted-foreground whitespace-nowrap">Scenario</th>
                    {syllabusActorIds.map((aid) => (
                      <th key={aid} className="px-1.5 py-2 font-medium text-muted-foreground text-center whitespace-nowrap min-w-[56px]">
                        {(actorMap.get(aid) ?? `#${aid}`).split(' ').pop()}
                      </th>
                    ))}
                    <th className="pl-3 py-2 font-medium text-muted-foreground text-right whitespace-nowrap">Progress</th>
                  </tr>
                </thead>
                <tbody>
                  {syllabus.items.map((item) => {
                    const actorEntries = syllabusActorIds.map((aid) => {
                      const completion = item.actors[aid];
                      const hasData = completion && 'grade' in completion;
                      return { aid, completion: hasData ? completion : null };
                    });
                    const done = actorEntries.filter((e) => e.completion?.grade).length;
                    const total = syllabusActorIds.length;
                    const pct = total > 0 ? (done / total) * 100 : 0;
                    return (
                      <tr key={item.scenario_id} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                        <td className="py-2.5 pr-3 font-medium whitespace-nowrap">{item.scenario_title}</td>
                        {actorEntries.map(({ aid, completion }) => {
                          if (!completion?.grade) {
                            return (
                              <td key={aid} className="px-1.5 py-2.5 text-center">
                                <span className="text-muted-foreground/30">—</span>
                              </td>
                            );
                          }
                          const grade = completion.grade;
                          const passing = grade <= (syllabus.min_grade ?? 'C');
                          return (
                            <td key={aid} className="px-1.5 py-2.5 text-center">
                              <span className={`inline-flex items-center justify-center h-6 min-w-[28px] px-1 rounded text-[10px] font-bold ${
                                passing
                                  ? 'bg-green-500/15 text-green-400 border border-green-500/30'
                                  : 'bg-red-500/10 text-red-400/70 border border-red-500/20'
                              }`}>
                                {grade}
                              </span>
                            </td>
                          );
                        })}
                        <td className="pl-3 py-2.5">
                          <div className="flex items-center gap-2 justify-end">
                            <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden">
                              <div className="h-full rounded-full bg-primary transition-all duration-500" style={{ width: `${pct}%` }} />
                            </div>
                            <span className="text-muted-foreground font-medium w-8 text-right">{done}/{total}</span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>

              {syllabus.level_complete && (
                <div className="rounded-lg bg-green-500/10 border border-green-500/30 p-4 text-center mt-4">
                  <p className="text-sm font-medium text-green-400">Level Complete! 🎓</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {level < 5 ? 'Take a reassessment to advance to the next level.' : 'You have mastered all levels!'}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-6">
              <p className="text-sm text-muted-foreground">No syllabus yet.</p>
              <Button size="sm" className="mt-3" onClick={() => navigate('/assessment')}>
                Take Assessment <ArrowRight className="ml-1 h-3 w-3" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Charts row */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Proficiency Radar */}
        {radarData.length > 0 ? (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Proficiency Radar</CardTitle>
              <CardDescription className="text-xs">Your current skill profile across key dimensions (0–100%)</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#3b3b3b" />
                  <PolarAngleAxis
                    dataKey="axis"
                    tick={({ x, y, payload }: { x: number; y: number; payload: { value: string; index: number } }) => {
                      const item = radarData[payload.index];
                      const color = DIMENSION_COLORS[item?.key] ?? '#a0a0a0';
                      return (
                        <text x={x} y={y} textAnchor="middle" dominantBaseline="central" fill={color} fontSize={11} fontWeight={500}>
                          {payload.value}
                        </text>
                      );
                    }}
                  />
                  <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                  {hasTargets && (
                    <Radar dataKey="target" stroke="#22c55e" strokeWidth={1.5} strokeDasharray="4 3" fill="none" fillOpacity={0} dot={false} />
                  )}
                  <Radar dataKey="value" stroke="#6264A7" fill="url(#radarGrad)" fillOpacity={0.5} />
                  <RechartsTooltip
                    position={{ x: 0, y: -10 }}
                    wrapperStyle={{ pointerEvents: 'none' }}
                    content={({ active, payload }) => {
                      if (!active || !payload?.length) return null;
                      const d = payload.find((p) => p.dataKey === 'value')?.payload as { axis: string; key: string; value: number; target?: number } | undefined;
                      if (!d) return null;
                      const tip = AXIS_TIPS[d.key];
                      return (
                        <div className="rounded-md bg-popover border p-2 text-xs shadow-md max-w-[220px]">
                          <p className="font-medium" style={{ color: DIMENSION_COLORS[d.key] ?? '#a0a0a0' }}>{d.axis}: {d.value}%</p>
                          {d.target != null && <p className="text-muted-foreground">Target: {d.target}%</p>}
                          {tip && <p className="text-muted-foreground mt-1">{tip}</p>}
                        </div>
                      );
                    }}
                  />
                  <defs>
                    <radialGradient id="radarGrad" cx="50%" cy="50%" r="50%">
                      <stop offset="0%" stopColor="#6264A7" stopOpacity={0.8} />
                      <stop offset="100%" stopColor="#6264A7" stopOpacity={0.15} />
                    </radialGradient>
                  </defs>
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
          <ScoreGrowthChart data={growthData} hasComposure={!!growth?.composure_trend && (growth.composure_trend as unknown[]).length > 0} targetScore={userTargets.overall} />
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
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Strengths &amp; Areas to Improve</CardTitle>
                <Button variant="ghost" size="sm" className="h-7 text-[10px] gap-1" onClick={openTargetEditor}>
                  <Crosshair className="h-3 w-3" /> {Object.keys(userTargets).length > 0 ? 'Edit targets' : 'Set targets'}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {editingTargets && (
                <div className="rounded-md border border-primary/30 bg-primary/5 p-3 space-y-2 mb-2">
                  <p className="text-xs font-medium">Set your target % for each dimension:</p>
                  {radarData.map((d) => (
                    <div key={d.key} className="flex items-center gap-2">
                      <span className="text-xs w-24 truncate" style={{ color: DIMENSION_COLORS[d.key] ?? '#aaa' }}>{d.axis}</span>
                      <input
                        type="range"
                        min={0}
                        max={100}
                        value={draftTargets[d.key] ?? 50}
                        onChange={(e) => setDraftTargets((p) => ({ ...p, [d.key]: Number(e.target.value) }))}
                        className="flex-1 h-1.5 accent-primary"
                      />
                      <span className="text-xs w-8 text-right">{draftTargets[d.key] ?? 50}%</span>
                    </div>
                  ))}
                  <div className="flex gap-2 pt-1">
                    <Button size="sm" className="h-6 text-[10px]" onClick={saveTargets} disabled={updateProfile.isPending}>Save</Button>
                    <Button size="sm" variant="ghost" className="h-6 text-[10px]" onClick={() => setEditingTargets(false)}>Cancel</Button>
                  </div>
                </div>
              )}
              {[...radarData].sort((a, b) => b.value - a.value).map((d, i) => {
                const isStrength = i < 2 && d.value >= 40;
                const isWeakness = i >= radarData.length - 1 || d.value < 30;
                const barColor = DIMENSION_COLORS[d.key] ?? '#6264A7';
                const target = userTargets[d.key];
                return (
                  <div key={d.axis} className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm" style={{ color: barColor }}>{d.axis}</span>
                      <div className="flex items-center gap-2">
                        {target != null && (
                          <span className="text-[10px] text-muted-foreground">
                            {d.value >= target ? '✓ target met' : `${target - d.value}% to target`}
                          </span>
                        )}
                        <span className="text-xs font-medium">{d.value}%</span>
                        {isStrength && <Badge variant="default" className="text-[10px] px-1.5 py-0">Strength</Badge>}
                        {isWeakness && <Badge variant="outline" className="text-[10px] px-1.5 py-0 border-amber-500/50 text-amber-400">Improve</Badge>}
                      </div>
                    </div>
                    <div className="relative h-1.5 w-full rounded-full bg-muted overflow-hidden">
                      <div className="h-full rounded-full transition-all" style={{ width: `${d.value}%`, backgroundColor: barColor }} />
                      {target != null && (
                        <div className="absolute top-0 h-full w-0.5 bg-white/60" style={{ left: `${Math.min(target, 100)}%` }} title={`Target: ${target}%`} />
                      )}
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        )}

        {/* Recommended Next + Grade Explanation */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recommended Next</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Grade explanation */}
            {growth?.average_score != null && (() => {
              const avg = Number(growth.average_score) || 0;
              const grade = SCORE_GRADE(avg);
              const info = GRADE_INFO[grade];
              return (
                <div className="rounded-md border p-3 space-y-1" style={{ borderColor: grade === 'S' ? '#f59e0b' : grade === 'A' ? '#10b981' : grade === 'B' ? '#3b82f6' : grade === 'C' ? '#8b5cf6' : '#ef4444' }}>
                  <p className="text-sm font-medium">Your Grade: {info?.label ?? grade}</p>
                  <p className="text-[10px] text-muted-foreground">{info?.desc}</p>
                  <p className="text-xs text-muted-foreground mt-1">{info?.tip}</p>
                </div>
              );
            })()}

            {/* Target-aware motivation */}
            {Object.keys(userTargets).length > 0 && radarData.length > 0 && (() => {
              const met = radarData.filter((d) => userTargets[d.key] != null && d.value >= userTargets[d.key]);
              const unmet = radarData.filter((d) => userTargets[d.key] != null && d.value < userTargets[d.key])
                .sort((a, b) => (userTargets[a.key] - a.value) - (userTargets[b.key] - b.value));
              return (
                <div className="rounded-md border border-card-border p-3 space-y-1">
                  {met.length > 0 && <p className="text-xs text-green-400">🎯 Targets met: {met.map((d) => d.axis).join(', ')}</p>}
                  {unmet.length > 0 && (
                    <p className="text-xs text-muted-foreground">
                      Closest target: {unmet[0].axis} — {userTargets[unmet[0].key] - unmet[0].value}% to go
                    </p>
                  )}
                </div>
              );
            })()}

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
        <PerspectiveEvolutionCard
          allStances={stancesEncountered}
          stanceTrend={(growth?.stance_trend ?? []) as Array<{ session_id: number; primary_stance: string; unique_stances: string[] }>}
          totalSessions={sessions?.length ?? 0}
        />
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
function ScoreGrowthChart({ data, hasComposure, targetScore }: { data: Array<Record<string, unknown>>; hasComposure: boolean; targetScore?: number }) {
  const [visibleLines, setVisibleLines] = useState<Set<string>>(() => {
    try {
      const saved = localStorage.getItem('growth-dims');
      if (saved) return new Set(JSON.parse(saved) as string[]);
    } catch { /* ignore */ }
    return new Set(['score']);
  });

  const toggle = (key: string) => {
    setVisibleLines((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        if (next.size > 1) next.delete(key); // keep at least one
      } else {
        next.add(key);
      }
      localStorage.setItem('growth-dims', JSON.stringify([...next]));
      return next;
    });
  };

  const dims = hasComposure ? GROWTH_DIMENSIONS : GROWTH_DIMENSIONS.filter((d) => d.key !== 'composure');

  // Custom tooltip
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    const score = payload.find((p: { dataKey: string }) => p.dataKey === 'score')?.value ?? 0;
    const date = payload[0]?.payload?.date;
    return (
      <div className="rounded-md bg-popover border p-2 text-xs shadow-md min-w-[140px]">
        <p className="font-medium text-popover-foreground mb-1">{label}{date ? ` — ${date}` : ''} — Grade {SCORE_GRADE(score)}</p>
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
            {targetScore != null && (
              <ReferenceLine y={targetScore} stroke="#22c55e" strokeDasharray="6 3" strokeWidth={1.5} label={{ value: `Target ${targetScore}%`, position: 'right', fill: '#22c55e', fontSize: 9 }} />
            )}
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

/* ── Perspective Evolution Card with time-based filtering ── */
type StanceTrendEntry = { session_id: number; primary_stance: string; unique_stances: string[] };
type StanceFilter = 'all' | 'last5' | 'last10';

const STANCE_FILTERS: { key: StanceFilter; label: string }[] = [
  { key: 'all', label: 'All Time' },
  { key: 'last5', label: 'Last 5' },
  { key: 'last10', label: 'Last 10' },
];

function PerspectiveEvolutionCard({
  allStances,
  stanceTrend,
  totalSessions,
}: {
  allStances: string[];
  stanceTrend: StanceTrendEntry[];
  totalSessions: number;
}) {
  const [filter, setFilter] = useState<StanceFilter>('all');

  // Filter stance trend
  const filteredTrend = (() => {
    if (filter === 'all' || stanceTrend.length === 0) return stanceTrend;
    const n = filter === 'last5' ? 5 : 10;
    return stanceTrend.slice(-n);
  })();

  // Derive stances from filtered trend or fall back to allStances
  const filteredStances = filteredTrend.length > 0
    ? [...new Set(filteredTrend.flatMap((e) => [e.primary_stance, ...e.unique_stances]))].sort()
    : allStances;

  // Count occurrences as primary stance
  const primaryCounts = new Map<string, number>();
  filteredTrend.forEach((e) => {
    primaryCounts.set(e.primary_stance, (primaryCounts.get(e.primary_stance) ?? 0) + 1);
  });

  // Generate narrative summary from stance data
  const stanceSummary = (() => {
    if (filteredTrend.length < 2) return null;
    const sorted = [...primaryCounts.entries()].sort((a, b) => b[1] - a[1]);
    const dominant = sorted[0]?.[0];
    const dominantCount = sorted[0]?.[1] ?? 0;
    const dominantPct = Math.round((dominantCount / filteredTrend.length) * 100);
    const recent = filteredTrend.slice(-3).map((e) => e.primary_stance);
    const recentUnique = [...new Set(recent)];
    const diversity = filteredStances.length;

    const parts: string[] = [];
    if (dominant) {
      parts.push(`Your dominant perspective is ${dominant} (${dominantPct}% of sessions).`);
    }
    if (diversity >= 4) {
      parts.push(`You\'ve explored ${diversity} different stances — strong epistemic diversity.`);
    } else if (diversity >= 2) {
      parts.push(`You\'ve encountered ${diversity} stances so far — try exploring more perspectives to broaden your range.`);
    }
    if (recentUnique.length >= 2) {
      parts.push(`Recently you\'ve been shifting between ${recentUnique.join(' and ')}, showing growing flexibility.`);
    } else if (recentUnique.length === 1 && recentUnique[0] !== dominant) {
      parts.push(`Your recent sessions show a shift toward ${recentUnique[0]}.`);
    }
    return parts.join(' ');
  })();

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <Eye className="h-4 w-4" /> Your Epistemological Perspectives
          </CardTitle>
          {stanceTrend.length > 0 && (
            <div className="flex gap-1">
              {STANCE_FILTERS.filter((f) => f.key === 'all' || (f.key === 'last5' && totalSessions >= 5) || (f.key === 'last10' && totalSessions >= 10)).map((f) => (
                <button
                  key={f.key}
                  onClick={() => setFilter(f.key)}
                  className={`text-[10px] px-2 py-0.5 rounded-full border transition-all ${
                    filter === f.key ? 'opacity-100 bg-primary/15 border-primary text-primary font-medium' : 'opacity-50 hover:opacity-80'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          )}
        </div>
        <CardDescription className="text-xs">
          {filter === 'all'
            ? 'Stances detected across all your conversations.'
            : `Stances from your ${filter === 'last5' ? 'last 5' : 'last 10'} sessions.`}
          {' '}As you practise, you&apos;ll explore more perspectives.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {stanceSummary && (
          <div className="rounded-md bg-primary/5 border border-primary/20 p-3">
            <p className="text-xs text-muted-foreground leading-relaxed">{stanceSummary}</p>
          </div>
        )}
        <div className="flex flex-wrap gap-2">
          {filteredStances.map((stance) => {
            const count = primaryCounts.get(stance);
            return (
              <Badge
                key={stance}
                variant="outline"
                className="text-xs px-2 py-1 border-2"
                style={{ borderColor: STANCE_COLORS[stance] ?? '#666', color: STANCE_COLORS[stance] ?? '#aaa' }}
              >
                {stance.charAt(0).toUpperCase() + stance.slice(1)}
                {count != null && count > 0 && <span className="ml-1 opacity-60">×{count}</span>}
              </Badge>
            );
          })}
          {filter === 'all' && filteredStances.length < 4 && (
            <Badge variant="outline" className="text-xs px-2 py-1 opacity-40 border-dashed">
              + {10 - filteredStances.length} more to discover
            </Badge>
          )}
        </div>
        <div className="space-y-2">
          {filteredStances.map((stance) => (
            <div key={stance} className="rounded-md border p-2.5 space-y-1">
              <div className="flex items-center gap-2">
                <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: STANCE_COLORS[stance] ?? '#666' }} />
                <span className="text-sm font-medium">{stance.charAt(0).toUpperCase() + stance.slice(1)}</span>
              </div>
              <p className="text-xs text-muted-foreground">{STANCE_DESCRIPTIONS[stance] ?? 'A unique epistemological perspective.'}</p>
            </div>
          ))}
        </div>
        {filteredStances.length < 3 && (
          <p className="text-xs text-muted-foreground italic">
            Tip: Try taking a different position in your next conversation. Deliberately argue from a perspective you wouldn&apos;t normally adopt.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
