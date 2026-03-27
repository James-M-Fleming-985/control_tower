import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/auth-store';
import { useSessionAnalysis, useSession, useActor } from '@/hooks/use-api';
import { WebSocketManager } from '@/lib/ws';
import { ChatBubble } from '@/components/conversation/chat-bubble';
import { ChatInput } from '@/components/conversation/chat-input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { GraduationCap, ArrowLeft, Sparkles, Award, Target, MessageSquare, TrendingUp } from 'lucide-react';
import { hornLabel } from '@/lib/utils';
import { HORN_COLORS } from '@/lib/constants';
import type { WSServerMessage } from '@/types/api';

const DIMENSION_LABELS: Record<string, { label: string; description: string }> = {
  gricean_score: { label: 'Gricean Quality', description: 'Clarity, relevance, truthfulness, detail' },
  trilemma_score: { label: 'Trilemma Navigation', description: 'Recognising and navigating the three horns' },
  flexibility_score: { label: 'Stance Flexibility', description: 'Exploring different epistemological stances' },
  engagement_score: { label: 'Engagement Depth', description: 'Depth and quality of your engagement' },
  composure_score: { label: 'Composure', description: 'Vocal composure and confidence (voice mode)' },
};

const GRADE_COLORS: Record<string, string> = {
  S: 'bg-amber-400 text-black',
  A: 'bg-green-500 text-white',
  B: 'bg-blue-500 text-white',
  C: 'bg-orange-500 text-white',
  D: 'bg-red-500 text-white',
};

interface DebriefMessage {
  role: 'user' | 'coach';
  content: string;
}

export function DebriefPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const accessToken = useAuthStore((s) => s.accessToken);

  const [messages, setMessages] = useState<DebriefMessage[]>([]);
  const [streamBuf, setStreamBuf] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [ended, setEnded] = useState(false);
  const [readOnly, setReadOnly] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [reward, setReward] = useState<Record<string, any> | null>(null);

  const wsRef = useRef<WebSocketManager | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Fetch session data for right panel
  const { data: session } = useSession(Number(sessionId) || 0);
  const { data: actor } = useActor(session?.actor_id ?? 0);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const navReward = (location.state as any)?.reward ?? null;
  const { data: analysisData } = useSessionAnalysis(Number(sessionId) || 0);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const analysis: any = reward?.analysis ?? navReward?.analysis ?? analysisData?.analysis;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const score: any = reward?.score ?? navReward?.score ?? analysisData?.score;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const proficiency: any = reward?.proficiency ?? navReward?.proficiency ?? null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const milestones: any = reward?.milestones ?? navReward?.milestones ?? null;

  useEffect(() => {
    if (!sessionId || !accessToken) return;

    const ws = new WebSocketManager(`/ws/debrief/${sessionId}`, {
      onMessage: (data: WSServerMessage) => {
        switch (data.type) {
          case 'debrief_start':
            break;
          case 'debrief_replay_message':
            setMessages((prev) => [
              ...prev,
              {
                role: data.role === 'user' ? 'user' : 'coach',
                content: data.content ?? '',
              },
            ]);
            break;
          case 'stream_start':
            setIsStreaming(true);
            setStreamBuf('');
            break;
          case 'stream_delta':
            setStreamBuf((prev) => prev + (data.content ?? ''));
            break;
          case 'stream_end':
            setStreamBuf((buf) => {
              if (buf) {
                setMessages((prev) => [...prev, { role: 'coach', content: buf }]);
              }
              return '';
            });
            setIsStreaming(false);
            break;
          case 'session_ended':
          case 'debrief_ended':
            if ('reward' in data && data.reward) {
              setReward(data.reward as Record<string, unknown>);
            }
            if (data.type === 'debrief_ended' && data.replay) {
              setReadOnly(true);
            }
            setEnded(true);
            break;
          case 'error':
            setError(data.detail ?? 'Something went wrong');
            break;
        }
      },
    });

    ws.connect();
    wsRef.current = ws;

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [sessionId, accessToken]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, streamBuf]);

  const sendMessage = useCallback((text: string) => {
    if (!wsRef.current || ended) return;
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    wsRef.current.sendJSON({ type: 'message', content: text });
  }, [ended]);

  const endDebrief = useCallback(() => {
    wsRef.current?.sendJSON({ type: 'end_debrief' });
  }, []);

  // Build dimension list from score
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

  if (error) {
    return (
      <div className="mx-auto max-w-2xl pt-12 text-center space-y-4">
        <p className="text-destructive">{error}</p>
        <Button variant="outline" onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-full gap-4">
      {/* Left column — chat */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-4 py-2">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/dashboard')} className="text-muted-foreground hover:text-foreground">
              <ArrowLeft className="h-4 w-4" />
            </button>
            <Badge variant="default" className="gap-1">
              <GraduationCap className="h-3 w-3" /> Coach Debrief
            </Badge>
            {actor && <span className="text-xs text-muted-foreground">Session with {actor.name}</span>}
          </div>
          {!ended && (
            <Button size="sm" variant="outline" onClick={endDebrief}>
              End Debrief
            </Button>
          )}
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {messages.length === 0 && !isStreaming && (
            <div className="text-center text-sm text-muted-foreground pt-8">
              Your coach is preparing the debrief…
            </div>
          )}
          {messages.map((m, i) => (
            <ChatBubble
              key={i}
              role={m.role === 'user' ? 'user' : 'actor'}
              content={m.content}
              actorName="Coach"
            />
          ))}
          {isStreaming && streamBuf && (
            <ChatBubble role="actor" content={streamBuf} actorName="Coach" isStreaming />
          )}
          {messages.length === 1 && messages[0].role === 'coach' && !isStreaming && !ended && (
            <div className="text-center text-xs text-muted-foreground/70 py-2">
              Reply to continue the debrief — ask about your strengths, weaknesses, or strategies for next time
            </div>
          )}
        </div>

        {/* Input */}
        {!ended && !readOnly ? (
          <ChatInput onSend={sendMessage} disabled={isStreaming} placeholder="Ask your coach about your session…" />
        ) : (
          <div className="border-t border-border px-4 py-3 flex items-center justify-center gap-3">
            {readOnly && (
              <span className="text-xs text-muted-foreground mr-2">Debrief Complete</span>
            )}
            <Button size="sm" onClick={() => navigate('/dashboard')}>
              View Dashboard
            </Button>
            <Button size="sm" variant="outline" onClick={() => navigate('/actors')}>
              New Conversation
            </Button>
          </div>
        )}
      </div>

      {/* Right panel — session results (hidden on mobile) */}
      <div className="hidden lg:flex w-80 shrink-0 flex-col gap-3 border-l border-border pl-4 overflow-y-auto py-3">
        {/* Score summary */}
        {score && (
          <Card>
            <CardHeader className="py-3 px-4">
              <CardTitle className="flex items-center gap-2 text-sm">
                <Award className="h-4 w-4 text-primary" /> Session Score
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3 space-y-3">
              <div className="flex items-end gap-2">
                <span className="text-3xl font-bold text-primary">{Math.round(score.final_score ?? score.total_score ?? 0)}</span>
                <span className="text-xs text-muted-foreground mb-1">/ 100</span>
                {score.grade && (
                  <Badge className={GRADE_COLORS[score.grade] ?? ''}>{score.grade}</Badge>
                )}
              </div>
              {dimensions.length > 0 && (
                <div className="space-y-2">
                  {dimensions.map((dim) => (
                    <div key={dim.key} className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="w-28 text-[10px] text-muted-foreground">{dim.label}</span>
                        <Progress value={dim.value} className="h-1.5 flex-1" />
                        <span className="text-[10px] w-6 text-right">{Math.round(dim.value)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Achievements */}
        {milestones?.newly_unlocked?.length > 0 && (
          <Card className="border-primary/50">
            <CardContent className="py-3 px-4">
              <p className="text-xs font-medium mb-2">🏆 Achievements Unlocked</p>
              <div className="flex flex-wrap gap-1">
                {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                {milestones.newly_unlocked.map((m: any) => (
                  <Badge key={m.id} variant="outline" className="text-[10px]">
                    {m.icon ?? '🏆'} {m.name}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Trilemma Journey */}
        {analysis && (
          <Card>
            <CardHeader className="py-3 px-4">
              <CardTitle className="flex items-center gap-2 text-sm">
                <Target className="h-3 w-3" /> Trilemma Journey
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3 space-y-2">
              {analysis.horn_sequence?.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {(analysis.horn_sequence as string[]).map((h: string, i: number) => (
                    <Badge key={i} className="text-[10px]" style={{ backgroundColor: HORN_COLORS[h] ?? '#6264A7', color: '#fff' }}>
                      {hornLabel(h)}
                    </Badge>
                  ))}
                </div>
              )}
              {analysis.dominant_stance && (
                <p className="text-[11px] text-muted-foreground">
                  Dominant: <span className="font-medium text-foreground capitalize">{String(analysis.dominant_stance).replace(/_/g, ' ')}</span>
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Coaching Summary */}
        {analysis?.coaching_summary && (
          <Card>
            <CardHeader className="py-3 px-4">
              <CardTitle className="flex items-center gap-2 text-sm">
                <MessageSquare className="h-3 w-3" /> Coaching Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <p className="text-[11px] text-muted-foreground leading-relaxed">{String(analysis.coaching_summary)}</p>
            </CardContent>
          </Card>
        )}

        {/* Proficiency */}
        {proficiency && (
          <Card>
            <CardHeader className="py-3 px-4">
              <CardTitle className="flex items-center gap-2 text-sm">
                <TrendingUp className="h-3 w-3" /> Proficiency
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3">
              <div className="space-y-2">
                {(['awareness', 'quality', 'flexibility', 'composure'] as const)
                  .filter((k) => proficiency[k]?.value != null)
                  .map((k) => (
                    <div key={k} className="flex items-center gap-2">
                      <span className="text-[10px] w-16 capitalize text-muted-foreground">{k}</span>
                      <Progress value={Math.round(proficiency[k].value * 100)} className="h-1.5 flex-1" />
                      <span className="text-[10px] w-8 text-right">{Math.round(proficiency[k].value * 100)}%</span>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Placeholder when no data yet */}
        {!score && !analysis && (
          <div className="text-center py-8">
            <Sparkles className="mx-auto h-6 w-6 text-muted-foreground/50 mb-2" />
            <p className="text-xs text-muted-foreground">Session results will appear here after the debrief</p>
          </div>
        )}
      </div>
    </div>
  );
}
