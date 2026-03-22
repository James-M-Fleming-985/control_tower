import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useScenarios, useActors, useCreateSession } from '@/hooks/use-api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { difficultyClass } from '@/lib/utils';
import { Search, Map } from 'lucide-react';

export function ScenariosPage() {
  const navigate = useNavigate();
  const { data: scenarios, isLoading } = useScenarios({});
  const { data: actors } = useActors();
  const createSession = useCreateSession();
  const [filter, setFilter] = useState('');

  const actorMap = Object.fromEntries((actors ?? []).map((a) => [a.id, a]));

  const filtered = (scenarios ?? []).filter(
    (s) =>
      s.title.toLowerCase().includes(filter.toLowerCase()) ||
      s.category.toLowerCase().includes(filter.toLowerCase()),
  );

  const startScenario = async (scenarioId: number, actorId?: number) => {
    if (!actorId) {
      navigate('/actors');
      return;
    }
    const session = await createSession.mutateAsync({
      actor_id: actorId,
      scenario_id: scenarioId,
      mode: 'text',
    });
    navigate(`/conversation/${session.id}`);
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
                onClick={() => startScenario(s.id, s.actor_id ?? undefined)}
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
                    {s.objectives?.length > 0 && (
                      <span className="text-xs text-muted-foreground ml-auto">{s.objectives.length} objectives</span>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
