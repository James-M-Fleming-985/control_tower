import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useScenarios, useActors, useCreateSession, useSyllabus } from '@/hooks/use-api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { difficultyClass } from '@/lib/utils';
import { Search, Map, X, CheckCircle2, MessageSquare, Mic } from 'lucide-react';
import type { ScenarioDefinition } from '@/types/api';

export function ScenariosPage() {
  const navigate = useNavigate();
  const { data: scenarios, isLoading } = useScenarios({});
  const { data: actors } = useActors();
  const createSession = useCreateSession();
  const [filter, setFilter] = useState('');
  const [pickActorFor, setPickActorFor] = useState<ScenarioDefinition | null>(null);
  const [sessionMode, setSessionMode] = useState<'text' | 'voice'>('text');
  const { data: syllabus } = useSyllabus();

  const actorMap = Object.fromEntries((actors ?? []).map((a) => [a.id, a]));
  const syllabusMap = Object.fromEntries(
    (syllabus?.scenarios ?? []).map((s) => [s.scenario_id, s]),
  );

  const filtered = (scenarios ?? []).filter(
    (s) =>
      s.title.toLowerCase().includes(filter.toLowerCase()) ||
      s.category.toLowerCase().includes(filter.toLowerCase()),
  );

  const startScenario = async (scenarioId: number, actorId: number, mode: 'text' | 'voice' = 'text') => {
    const session = await createSession.mutateAsync({
      actor_id: actorId,
      scenario_id: scenarioId,
      mode,
    });
    navigate(`/conversation/${session.id}`);
  };

  const handleScenarioClick = (scenario: ScenarioDefinition) => {
    if (scenario.actor_id) {
      startScenario(scenario.id, scenario.actor_id);
    } else {
      setPickActorFor(scenario);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Scenarios</h1>
        <p className="text-sm text-muted-foreground">Browse guided conversation scenarios</p>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Filter by title or category…"
          className="pl-9"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full rounded-sm" />
          ))}
        </div>
      ) : !filtered.length ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
            <Map className="h-10 w-10 mb-2" />
            <p>No scenarios match your filter</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {filtered.map((s) => {
            const actor = s.actor_id ? actorMap[s.actor_id] : undefined;
            return (
              <Card
                key={s.id}
                className="cursor-pointer transition-colors hover:border-primary/50"
                onClick={() => handleScenarioClick(s)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between gap-2">
                    <CardTitle className="text-sm truncate">{s.title}</CardTitle>
                    <Badge className={difficultyClass(s.difficulty)}>{s.difficulty}</Badge>
                  </div>
                  {s.description && <CardDescription className="text-xs line-clamp-2">{s.description}</CardDescription>}
                </CardHeader>
                <CardContent className="pb-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="outline" className="text-xs">{s.category}</Badge>
                    {actor && (
                      <span className="text-xs text-muted-foreground">with {actor.name}</span>
                    )}
                    {(() => {
                      const sp = syllabusMap[s.id];
                      if (sp) {
                        const done = sp.completed === sp.total;
                        return (
                          <Badge variant={done ? 'default' : 'outline'} className={`text-[10px] ml-auto ${done ? 'bg-green-600' : ''}`}>
                            {done && <CheckCircle2 className="h-3 w-3 mr-0.5" />}
                            {sp.completed}/{sp.total} actors
                          </Badge>
                        );
                      }
                      return s.objectives?.length > 0 ? (
                        <span className="text-xs text-muted-foreground ml-auto">{s.objectives.length} objectives</span>
                      ) : null;
                    })()}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Actor picker overlay */}
      {pickActorFor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setPickActorFor(null)}>
          <div className="bg-card border border-card-border rounded-lg p-6 max-w-md w-full mx-4 space-y-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Choose a discussion partner</h2>
              <button onClick={() => setPickActorFor(null)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>
            <p className="text-sm text-muted-foreground">
              Pick an actor for <span className="font-medium text-foreground">{pickActorFor.title}</span>
            </p>
            <div className="flex gap-2">
              <Button size="sm" variant={sessionMode === 'text' ? 'default' : 'outline'} onClick={() => setSessionMode('text')}>
                <MessageSquare className="h-3 w-3 mr-1" /> Text
              </Button>
              <Button size="sm" variant={sessionMode === 'voice' ? 'default' : 'outline'} onClick={() => setSessionMode('voice')}>
                <Mic className="h-3 w-3 mr-1" /> Voice
              </Button>
            </div>
            <div className="grid gap-2 max-h-60 overflow-auto">
              {(actors ?? []).map((a) => (
                <Button
                  key={a.id}
                  variant="outline"
                  className="justify-start h-auto py-3"
                  disabled={createSession.isPending}
                  onClick={() => startScenario(pickActorFor.id, a.id, sessionMode)}
                >
                  <div className="text-left">
                    <div className="font-medium">{a.name}</div>
                    <div className="text-xs text-muted-foreground">{a.epistemological_stance}</div>
                  </div>
                </Button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
