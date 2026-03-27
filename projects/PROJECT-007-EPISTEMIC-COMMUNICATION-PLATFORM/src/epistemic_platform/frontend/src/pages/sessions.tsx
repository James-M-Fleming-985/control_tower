import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSessions, useActors } from '@/hooks/use-api';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { History, GraduationCap, BarChart3, MessageSquare } from 'lucide-react';

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

export function SessionsPage() {
  const navigate = useNavigate();
  const { data: sessions, isLoading: loadingSessions } = useSessions();
  const { data: actors } = useActors();

  const actorMap = useMemo(() => {
    const m = new Map<number, string>();
    actors?.forEach((a) => m.set(a.id, a.name));
    return m;
  }, [actors]);

  // Separate parent sessions from debriefs
  const { parentSessions, debriefMap } = useMemo(() => {
    if (!sessions) return { parentSessions: [], debriefMap: new Map() };
    const parents = sessions.filter((s) => !s.parent_session_id);
    const dMap = new Map<number, typeof sessions[0]>();
    sessions
      .filter((s) => s.parent_session_id != null)
      .forEach((s) => {
        // Keep the most recent debrief per parent
        const existing = dMap.get(s.parent_session_id!);
        if (!existing || s.started_at > existing.started_at) {
          dMap.set(s.parent_session_id!, s);
        }
      });
    return { parentSessions: parents, debriefMap: dMap };
  }, [sessions]);

  // Group by date
  const grouped = useMemo(() => {
    const groups = new Map<string, typeof parentSessions>();
    parentSessions.forEach((s) => {
      const key = formatDate(s.started_at);
      const arr = groups.get(key) ?? [];
      arr.push(s);
      groups.set(key, arr);
    });
    return Array.from(groups.entries());
  }, [parentSessions]);

  if (loadingSessions) {
    return (
      <div className="mx-auto max-w-3xl space-y-4 pt-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  if (parentSessions.length === 0) {
    return (
      <div className="mx-auto max-w-3xl pt-12 text-center space-y-4">
        <History className="mx-auto h-12 w-12 text-muted-foreground/40" />
        <h2 className="text-lg font-semibold">No sessions yet</h2>
        <p className="text-sm text-muted-foreground">
          Complete a conversation to see your session history here.
        </p>
        <Button onClick={() => navigate('/actors')}>Start a Conversation</Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-3">
        <History className="h-5 w-5 text-primary" />
        <h1 className="text-xl font-bold">Session History</h1>
        <span className="text-sm text-muted-foreground">
          {parentSessions.length} session{parentSessions.length !== 1 ? 's' : ''}
        </span>
      </div>

      {grouped.map(([date, items]) => (
        <div key={date} className="space-y-3">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            {date}
          </h2>
          {items.map((session) => {
            const debrief = debriefMap.get(session.id);
            const actorName = actorMap.get(session.actor_id) ?? 'Unknown Actor';
            return (
              <Card key={session.id} className="hover:border-primary/30 transition-colors">
                <CardContent className="pt-4 pb-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-sm">{actorName}</span>
                      <Badge variant="outline" className="text-[10px]">
                        {session.mode}
                      </Badge>
                      <Badge
                        variant={session.status === 'completed' ? 'default' : 'outline'}
                        className="text-[10px]"
                      >
                        {session.status}
                      </Badge>
                    </div>
                    <span className="text-xs text-muted-foreground">{formatTime(session.started_at)}</span>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <MessageSquare className="h-3 w-3" />
                      {session.turn_count} turns
                    </span>
                    {debrief && (
                      <span className="flex items-center gap-1">
                        <GraduationCap className="h-3 w-3" />
                        Debrief {debrief.status === 'completed' ? 'complete' : 'in progress'}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2 pt-1">
                    {session.status === 'completed' && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-7 text-xs"
                        onClick={() => navigate(`/results/${session.id}`)}
                      >
                        <BarChart3 className="mr-1 h-3 w-3" /> Results
                      </Button>
                    )}
                    {debrief ? (
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-7 text-xs"
                        onClick={() => navigate(`/debrief/${session.id}`)}
                      >
                        <GraduationCap className="mr-1 h-3 w-3" />
                        {debrief.status === 'completed' ? 'View Debrief' : 'Resume Debrief'}
                      </Button>
                    ) : session.status === 'completed' ? (
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-7 text-xs"
                        onClick={() => navigate(`/debrief/${session.id}`)}
                      >
                        <GraduationCap className="mr-1 h-3 w-3" /> Start Debrief
                      </Button>
                    ) : null}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ))}
    </div>
  );
}
