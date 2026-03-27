import { useNavigate, useParams } from 'react-router-dom';
import { useActor, useScenarios, useCreateSession, useSyllabus } from '@/hooks/use-api';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { stanceLabel, difficultyClass } from '@/lib/utils';
import { STANCE_COLORS } from '@/lib/constants';
import { ArrowLeft, MessageSquare, Mic, CheckCircle2 } from 'lucide-react';

export function ActorDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: actor, isLoading: actorLoading } = useActor(Number(id));
  const { data: scenarios, isLoading: scenariosLoading } = useScenarios({ category: undefined, difficulty: undefined });
  const createSession = useCreateSession();
  const { data: syllabus } = useSyllabus();

  const actorScenarios = scenarios?.filter((s) => s.actor_id === Number(id) || !s.actor_id) || [];

  // Build a lookup: scenario_id → actor completion status for this actor
  const syllabusItems = syllabus?.items ?? [];
  const actorCompletionMap = Object.fromEntries(
    syllabusItems.map((item) => {
      const actorKey = String(id);
      const completion = actorKey && item.actors?.[actorKey];
      return [item.scenario_id, completion && 'grade' in completion ? completion : null];
    }),
  );

  const startSession = async (mode: 'text' | 'voice', scenarioId?: number) => {
    const session = await createSession.mutateAsync({
      actor_id: Number(id),
      scenario_id: scenarioId,
      mode,
    });
    navigate(`/conversation/${session.id}`);
  };

  if (actorLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (!actor) return <p className="text-muted-foreground">Actor not found</p>;

  const stanceColor = STANCE_COLORS[actor.epistemological_stance] ?? '#6264A7';

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <button onClick={() => navigate('/actors')} className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Back to actors
      </button>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <div
              className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full text-lg font-bold text-white"
              style={{ backgroundColor: stanceColor }}
            >
              {actor.name.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-xl font-bold">{actor.name}</h1>
              <Badge variant="outline" className="mt-1 capitalize">{stanceLabel(actor.epistemological_stance)}</Badge>
              {actor.description && <p className="mt-3 text-sm text-muted-foreground">{actor.description}</p>}
              {actor.archetype && (
                <span className="mt-2 inline-block text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                  {actor.archetype}
                </span>
              )}
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <Button onClick={() => startSession('text')} disabled={createSession.isPending}>
              <MessageSquare className="mr-2 h-4 w-4" />
              Start Text Chat
            </Button>
            <Button variant="outline" onClick={() => startSession('voice')} disabled={createSession.isPending}>
              <Mic className="mr-2 h-4 w-4" />
              Start Voice Chat
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Scenarios */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Available Scenarios</h2>
        {scenariosLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        ) : !actorScenarios.length ? (
          <p className="text-sm text-muted-foreground">No scenarios — start a free-form conversation above.</p>
        ) : (
          <div className="space-y-3">
            {actorScenarios.map((s) => {
              const completion = actorCompletionMap[s.id];
              return (
              <Card key={s.id} className="hover:border-primary/50 transition-colors">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm flex items-center gap-1.5">
                      {completion && <CheckCircle2 className="h-3.5 w-3.5 text-green-400 shrink-0" />}
                      {s.title}
                    </CardTitle>
                    <Badge className={difficultyClass(s.difficulty)}>{s.difficulty}</Badge>
                  </div>
                  {s.description && <CardDescription className="text-xs">{s.description}</CardDescription>}
                </CardHeader>
                <CardContent className="pb-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">{s.category}</Badge>
                    {completion && (
                      <Badge variant="outline" className="text-[10px] text-green-400 border-green-400/50">
                        {completion.grade}
                      </Badge>
                    )}
                    <div className="flex gap-1.5 ml-auto">
                      <Button size="sm" variant="ghost" className="h-7 px-2 text-xs" disabled={createSession.isPending} onClick={() => startSession('text', s.id)}>
                        <MessageSquare className="h-3 w-3 mr-1" /> Text
                      </Button>
                      <Button size="sm" variant="ghost" className="h-7 px-2 text-xs" disabled={createSession.isPending} onClick={() => startSession('voice', s.id)}>
                        <Mic className="h-3 w-3 mr-1" /> Voice
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
