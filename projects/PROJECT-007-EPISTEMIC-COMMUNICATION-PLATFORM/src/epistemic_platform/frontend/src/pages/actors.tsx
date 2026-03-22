import { useNavigate } from 'react-router-dom';
import { useActors } from '@/hooks/use-api';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { stanceLabel } from '@/lib/utils';
import { STANCE_COLORS } from '@/lib/constants';
import { Users } from 'lucide-react';
import type { ActorProfile } from '@/types/api';

export function ActorsPage() {
  const navigate = useNavigate();
  const { data: actors, isLoading } = useActors();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Conversation Partners</h1>
        <p className="text-sm text-muted-foreground">Choose an actor to practice epistemic dialogue with</p>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-sm" />
          ))}
        </div>
      ) : !actors?.length ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
            <Users className="h-10 w-10 mb-2" />
            <p>No actors available yet</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {actors.map((actor: ActorProfile) => {
            const stanceColor = STANCE_COLORS[actor.epistemological_stance] ?? '#6264A7';
            return (
              <Card
                key={actor.id}
                className="cursor-pointer transition-colors hover:border-primary/50"
                onClick={() => navigate(`/actors/${actor.id}`)}
              >
                <CardContent className="pt-5 space-y-3">
                  <div className="flex items-start gap-3">
                    <div
                      className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
                      style={{ backgroundColor: stanceColor }}
                    >
                      {actor.name.charAt(0)}
                    </div>
                    <div className="min-w-0">
                      <h3 className="font-semibold truncate">{actor.name}</h3>
                      <Badge variant="outline" className="mt-1 text-xs capitalize">
                        {stanceLabel(actor.epistemological_stance)}
                      </Badge>
                    </div>
                  </div>
                  {actor.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2">{actor.description}</p>
                  )}
                  {actor.archetype && (
                    <span className="inline-block text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                      {actor.archetype}
                    </span>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
