import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useSessionAnalysis, useSession, useActor } from '@/hooks/use-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { hornLabel, stanceLabel, formatDuration } from '@/lib/utils';
import { HORN_COLORS } from '@/lib/constants';
import { ArrowLeft, Award, MessageSquare, Target, GraduationCap, TrendingUp, Sparkles } from 'lucide-react';

const GRADE_COLORS: Record<string, string> = {
  S: 'bg-amber-400 text-black',
  A: 'bg-green-500 text-white',
  B: 'bg-blue-500 text-white',
  C: 'bg-orange-500 text-white',
  D: 'bg-red-500 text-white',
};

const DIMENSION_LABELS: Record<string, { label: string; description: string }> = {
  gricean_score: {
    label: 'Gricean Quality',
    description: 'How well you followed conversational maxims — clarity, relevance, truthfulness, and appropriate detail',
  },
  trilemma_score: {
    label: 'Trilemma Navigation',
    description: 'Your ability to recognise and navigate between the three horns of the epistemic trilemma',
  },
  flexibility_score: {
    label: 'Stance Flexibility',
    description: 'How well you explored and shifted between different epistemological stances during the conversation',
  },
  engagement_score: {
    label: 'Engagement Depth',
    description: 'The depth and quality of your engagement with the topic and your conversation partner',
  },
  composure_score: {
    label: 'Composure',
    description: 'Your vocal composure and confidence during the conversation (voice mode only)',
  },
};

export function ResultsPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { data: session } = useSession(Number(sessionId) || 0);
  const { data: actor } = useActor(session?.actor_id ?? 0);

  // Use reward data from navigation state (passed from conversation page) if available
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const navReward = (location.state as any)?.reward ?? null;

  // Fall back to on-demand analytics API for historical sessions
  const { data, isLoading } = useSessionAnalysis(Number(sessionId) || 0);

  // Merge: prefer navigation reward, fall back to API data
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const analysis: any = navReward?.analysis ?? data?.analysis;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const score: any = navReward?.score ?? data?.score;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const xpAward: any = navReward?.xp_award ?? null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const milestones: any = navReward?.milestones ?? null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const proficiency: any = navReward?.proficiency ?? null;

  if (isLoading && !navReward) {
    return (
      <div className="mx-auto max-w-3xl space-y-4 pt-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  // Build dimension list from score object (backend uses individual fields, not a "dimensions" sub-object)
  const dimensions = score
    ? (['gricean_score', 'trilemma_score', 'flexibility_score', 'engagement_score', 'composure_score'] as const)
        .filter((k) => score[k] != null)
        .map((k) => ({
          key: k,
          label: DIMENSION_LABELS[k]?.label ?? k.replace(/_/g, ' '),
          description: DIMENSION_LABELS[k]?.description ?? '',
          value: Number(score[k]),
        }))
    : [];

  // Also support the legacy "dimensions" sub-object from analytics API
  const legacyDimensions = score?.dimensions
    ? Object.entries(score.dimensions as Record<string, number>).map(([k, v]) => ({
        key: k,
        label: DIMENSION_LABELS[k]?.label ?? k.replace(/_/g, ' '),
        description: DIMENSION_LABELS[k]?.description ?? '',
        value: Number(v),
      }))
    : [];

  const allDimensions = dimensions.length > 0 ? dimensions : legacyDimensions;
  const finalScore = score?.final_score ?? score?.total_score ?? 0;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/actors')} className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h1 className="text-xl font-bold">Session Results</h1>
          {actor && <p className="text-sm text-muted-foreground">Conversation with {actor.name}</p>}
        </div>
      </div>

      {/* Overall score */}
      {score && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Award className="h-4 w-4 text-primary" /> Overall Score
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-end gap-3">
              <span className="text-4xl font-bold text-primary">{Math.round(finalScore)}</span>
              <span className="text-sm text-muted-foreground mb-1">/ 100</span>
              {score.grade && (
                <Badge className={GRADE_COLORS[score.grade] ?? ''}>{score.grade}</Badge>
              )}
            </div>

            {/* XP earned */}
            {xpAward && (
              <div className="flex items-center gap-3 text-sm">
                <Sparkles className="h-4 w-4 text-primary" />
                <span className="font-medium text-primary">+{xpAward.total} XP earned</span>
                {xpAward.improvement_bonus > 0 && (
                  <span className="text-xs text-muted-foreground">(includes +{xpAward.improvement_bonus} improvement bonus)</span>
                )}
                {xpAward.levelled_up && (
                  <Badge className="bg-amber-400 text-black">Level Up!</Badge>
                )}
              </div>
            )}

            {/* Dimension breakdown with tooltips */}
            {allDimensions.length > 0 && (
              <div className="space-y-3 pt-2">
                {allDimensions.map((dim) => (
                  <div key={dim.key} className="space-y-1">
                    <div className="flex items-center gap-3">
                      <span className="w-40 text-xs font-medium text-muted-foreground">{dim.label}</span>
                      <Progress value={dim.value} className="h-2 flex-1" />
                      <span className="text-xs text-muted-foreground w-8 text-right">{Math.round(dim.value)}</span>
                    </div>
                    {dim.description && (
                      <p className="ml-40 pl-3 text-[10px] text-muted-foreground/70">{dim.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Newly unlocked milestones */}
      {milestones?.newly_unlocked?.length > 0 && (
        <Card className="border-primary/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              🏆 Achievements Unlocked!
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
              {milestones.newly_unlocked.map((m: any) => (
                <Badge key={m.id} variant="default" className="text-xs gap-1">
                  {m.icon ?? '🏆'} {m.name}
                  {m.xp_reward > 0 && <span className="text-primary">+{m.xp_reward} XP</span>}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis highlights */}
      {analysis && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Target className="h-4 w-4" /> Trilemma Journey
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {analysis.horn_sequence?.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {(analysis.horn_sequence as string[]).map((h: string, i: number) => (
                    <Badge key={i} style={{ backgroundColor: HORN_COLORS[h] ?? '#6264A7', color: '#fff' }}>
                      {hornLabel(h)}
                    </Badge>
                  ))}
                </div>
              )}
              {analysis.dominant_stance && (
                <p className="text-sm text-muted-foreground">
                  Dominant stance: <span className="font-medium text-foreground capitalize">{stanceLabel(String(analysis.dominant_stance))}</span>
                </p>
              )}
              {analysis.turn_count !== undefined && (
                <p className="text-sm text-muted-foreground">
                  {Number(analysis.turn_count) || 0} turns
                  {session?.started_at && session?.ended_at && (
                    <> · {formatDuration(session.started_at, session.ended_at)}</>
                  )}
                </p>
              )}
            </CardContent>
          </Card>

          {analysis.coaching_summary && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <MessageSquare className="h-4 w-4" /> Coaching Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground leading-relaxed">{String(analysis.coaching_summary)}</p>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* Proficiency change */}
      {proficiency && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <TrendingUp className="h-4 w-4" /> Proficiency Update
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {(['awareness', 'quality', 'flexibility', 'composure'] as const)
                .filter((k) => proficiency[k]?.value != null)
                .map((k) => (
                  <div key={k} className="space-y-1">
                    <span className="text-xs font-medium capitalize text-muted-foreground">{k}</span>
                    <div className="flex items-center gap-2">
                      <Progress value={Math.round(proficiency[k].value * 100)} className="h-2 flex-1" />
                      <span className="text-xs font-medium">{Math.round(proficiency[k].value * 100)}%</span>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        <Button onClick={() => navigate(`/debrief/${sessionId}`)}>
          <GraduationCap className="mr-1 h-4 w-4" /> Start Coach Debrief
        </Button>
        <Button variant="outline" onClick={() => navigate('/actors')}>
          New Conversation
        </Button>
        <Button variant="ghost" onClick={() => navigate('/dashboard')}>
          View Dashboard
        </Button>
      </div>
    </div>
  );
}
