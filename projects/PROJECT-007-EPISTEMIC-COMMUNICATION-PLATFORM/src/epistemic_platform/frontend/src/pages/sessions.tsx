import { useMemo, useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSessions, useActors, useSession } from '@/hooks/use-api';
import { ChatBubble } from '@/components/conversation/chat-bubble';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { History, GraduationCap, BarChart3, MessageSquare, ScrollText, X, Play } from 'lucide-react';

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
  const [transcriptId, setTranscriptId] = useState<number | null>(null);
  const { data: transcriptSession, isLoading: transcriptLoading } = useSession(transcriptId ?? 0);
  const transcriptScrollRef = useRef<HTMLDivElement>(null);

  // Scroll transcript to bottom when loaded
  useEffect(() => {
    if (transcriptSession?.messages?.length) {
      setTimeout(() => {
        transcriptScrollRef.current?.scrollTo({ top: 0 });
      }, 50);
    }
  }, [transcriptSession]);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setTranscriptId(null);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

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
    <div className="flex h-full gap-0">
      {/* Left: session list */}
      <div className={`flex-1 min-w-0 overflow-y-auto transition-all duration-300 ${transcriptId ? 'pr-0' : ''}`}>
        <div className="mx-auto max-w-3xl space-y-6 px-4 py-2">
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
                const isSelected = transcriptId === session.id;
                return (
                  <Card key={session.id} className={`transition-colors ${isSelected ? 'border-primary/50 bg-primary/5' : 'hover:border-primary/30'}`}>
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
                        {session.status === 'active' && (
                          <Button
                            size="sm"
                            variant="default"
                            className="h-7 text-xs"
                            onClick={() => navigate(`/conversation/${session.id}`)}
                          >
                            <Play className="mr-1 h-3 w-3" /> Resume
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant={isSelected ? 'default' : 'outline'}
                          className="h-7 text-xs"
                          onClick={() => setTranscriptId(isSelected ? null : session.id)}
                        >
                          <ScrollText className="mr-1 h-3 w-3" /> Transcript
                        </Button>
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
      </div>

      {/* Right: transcript slide-out panel */}
      {transcriptId && (
        <div className="w-[420px] shrink-0 border-l border-border flex flex-col bg-background animate-in slide-in-from-right duration-200">
          {/* Panel header */}
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <div className="flex items-center gap-2 min-w-0">
              <ScrollText className="h-4 w-4 text-primary shrink-0" />
              <div className="min-w-0">
                <p className="text-sm font-medium truncate">
                  {actorMap.get(transcriptSession?.actor_id ?? 0) ?? 'Conversation'}
                </p>
                <p className="text-[10px] text-muted-foreground">
                  {transcriptSession?.started_at ? formatDate(transcriptSession.started_at) + ' · ' + formatTime(transcriptSession.started_at) : ''}
                  {transcriptSession?.mode ? ` · ${transcriptSession.mode}` : ''}
                </p>
              </div>
            </div>
            <button
              onClick={() => setTranscriptId(null)}
              className="p-1 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Panel body */}
          <div ref={transcriptScrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
            {transcriptLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-12 w-3/4" />
                <Skeleton className="h-12 w-2/3 ml-auto" />
                <Skeleton className="h-12 w-3/4" />
              </div>
            ) : transcriptSession?.messages?.length ? (
              transcriptSession.messages.map((msg, i) => (
                <ChatBubble
                  key={i}
                  role={msg.role === 'user' ? 'user' : 'actor'}
                  content={msg.content}
                  timestamp={msg.timestamp}
                  actorName={actorMap.get(transcriptSession.actor_id) ?? 'Actor'}
                />
              ))
            ) : (
              <p className="text-sm text-muted-foreground text-center pt-8">No messages in this session.</p>
            )}
          </div>

          {/* Panel footer */}
          <div className="border-t border-border px-4 py-2 flex items-center justify-between">
            <span className="text-[10px] text-muted-foreground">
              {transcriptSession?.messages?.length ?? 0} messages · {transcriptSession?.turn_count ?? 0} turns
            </span>
            {transcriptSession?.status === 'active' ? (
              <Button size="sm" variant="default" className="h-6 text-[10px]" onClick={() => navigate(`/conversation/${transcriptId}`)}>
                <Play className="mr-1 h-3 w-3" /> Resume
              </Button>
            ) : transcriptSession?.status === 'completed' ? (
              <Button size="sm" variant="outline" className="h-6 text-[10px]" onClick={() => navigate(`/debrief/${transcriptId}`)}>
                Open Debrief
              </Button>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}
