import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuthStore } from '@/stores/auth-store';
import { WebSocketManager } from '@/lib/ws';
import { ChatBubble } from '@/components/conversation/chat-bubble';
import { ChatInput } from '@/components/conversation/chat-input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { GraduationCap, ArrowLeft } from 'lucide-react';
import type { WSServerMessage } from '@/types/api';

interface DebriefMessage {
  role: 'user' | 'coach';
  content: string;
}

export function DebriefPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const accessToken = useAuthStore((s) => s.accessToken);

  const [messages, setMessages] = useState<DebriefMessage[]>([]);
  const [streamBuf, setStreamBuf] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [ended, setEnded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocketManager | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sessionId || !accessToken) return;

    const ws = new WebSocketManager(`/ws/debrief/${sessionId}`, {
      onMessage: (data: WSServerMessage) => {
        switch (data.type) {
          case 'debrief_start':
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

  if (error) {
    return (
      <div className="mx-auto max-w-2xl pt-12 text-center space-y-4">
        <p className="text-destructive">{error}</p>
        <Button variant="outline" onClick={() => navigate(`/results/${sessionId}`)}>
          Back to Results
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-2">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(`/results/${sessionId}`)} className="text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
          </button>
          <Badge variant="default" className="gap-1">
            <GraduationCap className="h-3 w-3" /> Coach Debrief
          </Badge>
          <span className="text-xs text-muted-foreground">Premium</span>
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
      </div>

      {/* Input */}
      {!ended ? (
        <ChatInput onSend={sendMessage} disabled={isStreaming} />
      ) : (
        <div className="border-t border-border px-4 py-3 text-center text-sm text-muted-foreground">
          Debrief complete.{' '}
          <button onClick={() => navigate('/dashboard')} className="text-primary hover:underline">
            View Dashboard →
          </button>
        </div>
      )}
    </div>
  );
}
