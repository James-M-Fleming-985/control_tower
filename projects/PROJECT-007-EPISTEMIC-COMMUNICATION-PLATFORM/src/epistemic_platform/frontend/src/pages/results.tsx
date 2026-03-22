import { useNavigate, useParams } from 'react-router-dom';
import { useSessionAnalysis, useSession, useActor } from '@/hooks/use-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { hornLabel, stanceLabel, formatDuration } from '@/lib/utils';
import { HORN_COLORS } from '@/lib/constants';
import { ArrowLeft, Award, MessageSquare, Target } from 'lucide-react';

export function ResultsPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { data: session } = useSession(Number(sessionId) || 0);
  const { data: actor } = useActor(session?.actor_id ?? 0);
  const { data, isLoading } = useSessionAnalysis(Number(sessionId) || 0);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-4 pt-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const analysis: any = data?.analysis;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const score: any = data?.score;

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
          <CardContent className="space-y-3">
            <div className="flex items-end gap-3">
              <span className="text-4xl font-bold text-primary">{score.total_score ?? 0}</span>
              <span className="text-sm text-muted-foreground mb-1">/ 100</span>
              {score.grade && <Badge>{score.grade}</Badge>}
            </div>
            {score.xp_earned !== undefined && (
              <p className="text-sm text-muted-foreground">+{score.xp_earned} XP earned</p>
            )}

            {/* Dimension breakdown */}
            {score.dimensions && (
              <div className="space-y-2 pt-2">
                {Object.entries(score.dimensions as Record<string, number>).map(([dim, val]) => (
                  <div key={dim} className="flex items-center gap-3">
                    <span className="w-36 text-xs capitalize text-muted-foreground">{dim.replace(/_/g, ' ')}</span>
                    <Progress value={val} className="h-2 flex-1" />
                    <span className="text-xs text-muted-foreground w-8 text-right">{Math.round(val)}</span>
                  </div>
                ))}
              </div>
            )}
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

      {/* Actions */}
      <div className="flex flex-wrap gap-3">
        <Button onClick={() => navigate(`/debrief/${sessionId}`)}>
          Start Coach Debrief
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
