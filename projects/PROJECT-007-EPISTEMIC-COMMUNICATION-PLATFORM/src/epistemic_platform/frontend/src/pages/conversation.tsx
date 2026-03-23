import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useSession, useActor } from '@/hooks/use-api';
import { useAuthStore } from '@/stores/auth-store';
import { WebSocketManager } from '@/lib/ws';
import { ChatBubble } from '@/components/conversation/chat-bubble';
import { ChatInput } from '@/components/conversation/chat-input';
import { CoachingPanel } from '@/components/conversation/coaching-panel';
import { TrilemmaVisual } from '@/components/conversation/trilemma-visual';
import { VoiceOrb } from '@/components/voice/voice-orb';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, Mic, StopCircle } from 'lucide-react';
import type { ChatMessage, CoachingAnnotation, TrilemmaState, HornDetection, StanceDetection, WSServerMessage } from '@/types/api';

interface LocalMessage {
  role: 'user' | 'actor';
  content: string;
  timestamp: string;
}

type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking';

export function ConversationPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const accessToken = useAuthStore((s) => s.accessToken);
  const { data: session, isLoading: sessionLoading } = useSession(Number(sessionId) || 0);
  const { data: actor } = useActor(session?.actor_id ?? 0);
  const isVoice = session?.mode === 'voice';

  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [streamBuf, setStreamBuf] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [annotations, setAnnotations] = useState<CoachingAnnotation[]>([]);
  const [trilemmaState, setTrilemmaState] = useState<TrilemmaState | null>(null);
  const [lastHorn, setLastHorn] = useState<HornDetection | null>(null);
  const [lastStance, setLastStance] = useState<StanceDetection | null>(null);
  const [ended, setEnded] = useState(false);

  // Voice-specific state
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [recording, setRecording] = useState(false);

  const wsRef = useRef<WebSocketManager | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioQueueRef = useRef<ArrayBuffer[]>([]);
  const isPlayingRef = useRef(false);

  // Load existing messages from session
  useEffect(() => {
    if (!session) return;
    if (session.status !== 'active') setEnded(true);
    if (session.messages?.length) {
      setMessages(
        session.messages.map((m: ChatMessage) => ({
          role: m.role === 'user' ? 'user' as const : 'actor' as const,
          content: m.content,
          timestamp: m.timestamp ?? new Date().toISOString(),
        })),
      );
    }
    if (session.coaching_annotations?.length) {
      setAnnotations(session.coaching_annotations as CoachingAnnotation[]);
    }
    if (session.trilemma_state) {
      setTrilemmaState(session.trilemma_state as TrilemmaState);
    }
  }, [session]);

  // --- Audio playback helpers ---
  const playNextChunk = useCallback(async () => {
    if (isPlayingRef.current || audioQueueRef.current.length === 0) return;
    isPlayingRef.current = true;
    const chunk = audioQueueRef.current.shift()!;
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }
      const ctx = audioContextRef.current;
      const buffer = await ctx.decodeAudioData(chunk.slice(0));
      const source = ctx.createBufferSource();
      source.buffer = buffer;
      source.connect(ctx.destination);
      source.onended = () => {
        isPlayingRef.current = false;
        playNextChunk();
      };
      source.start();
    } catch {
      isPlayingRef.current = false;
      playNextChunk();
    }
  }, []);

  const enqueueAudio = useCallback((data: ArrayBuffer) => {
    audioQueueRef.current.push(data);
    playNextChunk();
  }, [playNextChunk]);

  const stopPlayback = useCallback(() => {
    audioQueueRef.current = [];
    isPlayingRef.current = false;
  }, []);

  // --- WebSocket message handler ---
  const handleWsMessage = useCallback((data: WSServerMessage) => {
    switch (data.type) {
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
            setMessages((prev) => [
              ...prev,
              { role: 'actor', content: buf, timestamp: new Date().toISOString() },
            ]);
          }
          return '';
        });
        setIsStreaming(false);
        break;
      case 'trilemma_update':
        if (data.state) setTrilemmaState(data.state as TrilemmaState);
        if (data.horn_detection) setLastHorn(data.horn_detection as HornDetection);
        break;
      case 'stance_update':
        if (data.detection) setLastStance(data.detection as StanceDetection);
        break;
      case 'coaching':
        if (data.annotation) {
          setAnnotations((prev) => [...prev, data.annotation as CoachingAnnotation]);
        }
        break;
      case 'transcription':
        if ('text' in data) {
          setMessages((prev) => [
            ...prev,
            { role: 'user', content: data.text, timestamp: new Date().toISOString() },
          ]);
        }
        break;
      case 'state_change':
        if ('state' in data) {
          setVoiceState(data.state as VoiceState);
        }
        break;
      case 'audio_end':
        setVoiceState('idle');
        break;
      case 'barge_in':
        stopPlayback();
        break;
      case 'session_ended':
        setEnded(true);
        break;
      case 'error':
        console.error('WS error:', (data as { detail: string }).detail);
        break;
    }
  }, [stopPlayback]);

  // --- Connect WebSocket ---
  useEffect(() => {
    if (!sessionId || !accessToken || ended || !session) return;

    const wsPath = isVoice
      ? `/ws/voice/${sessionId}`
      : `/ws/conversation/${sessionId}`;

    const ws = new WebSocketManager(wsPath, {
      onMessage: handleWsMessage,
      onBinary: isVoice ? enqueueAudio : undefined,
    });

    ws.connect();
    wsRef.current = ws;

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [sessionId, accessToken, ended, isVoice, session, handleWsMessage, enqueueAudio]);

  // Cleanup audio context on unmount
  useEffect(() => {
    return () => {
      audioContextRef.current?.close();
      mediaRecorderRef.current?.stop();
    };
  }, []);

  // Auto-scroll
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, streamBuf]);

  // --- Recording controls ---
  const startRecording = useCallback(async () => {
    if (!wsRef.current) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : 'audio/webm',
      });
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0 && wsRef.current) {
          e.data.arrayBuffer().then((buf) => wsRef.current?.send(buf));
        }
      };
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
      };
      recorder.start(250); // 250ms chunks
      mediaRecorderRef.current = recorder;
      setRecording(true);
      setVoiceState('listening');
    } catch (err) {
      console.error('Microphone access denied:', err);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    mediaRecorderRef.current = null;
    setRecording(false);
    if (wsRef.current) {
      wsRef.current.sendJSON({ type: 'audio_end' });
    }
  }, []);

  const toggleRecording = useCallback(() => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [recording, startRecording, stopRecording]);

  const sendMessage = useCallback(
    (text: string) => {
      if (!wsRef.current || ended) return;
      const now = new Date().toISOString();
      setMessages((prev) => [...prev, { role: 'user', content: text, timestamp: now }]);
      wsRef.current.sendJSON({ type: 'message', content: text });
    },
    [ended],
  );

  const endSession = useCallback(() => {
    if (!wsRef.current) return;
    wsRef.current.sendJSON({ type: 'end_session' });
  }, []);

  if (sessionLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Skeleton className="h-96 w-full max-w-3xl" />
      </div>
    );
  }

  return (
    <div className="flex h-full gap-4">
      {/* Chat area */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header bar */}
        <div className="flex items-center justify-between border-b border-border px-4 py-2">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/actors')}
              className="text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
            </button>
            <span className="font-semibold text-sm">{actor?.name ?? 'Actor'}</span>
            {lastStance && (
              <Badge variant="outline" className="text-xs capitalize">
                {lastStance.stance}
              </Badge>
            )}
            {isVoice && (
              <Badge variant="default" className="text-xs">
                <Mic className="mr-1 h-3 w-3" /> Voice
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            {!ended && (
              <Button size="sm" variant="destructive" onClick={endSession}>
                <StopCircle className="mr-1 h-3 w-3" /> End
              </Button>
            )}
            {ended && (
              <Button size="sm" onClick={() => navigate(`/results/${sessionId}`)}>
                View Results
              </Button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {messages.map((m, i) => (
            <ChatBubble
              key={i}
              role={m.role}
              content={m.content}
              timestamp={m.timestamp}
              actorName={actor?.name}
            />
          ))}
          {isStreaming && streamBuf && (
            <ChatBubble
              role="actor"
              content={streamBuf}
              actorName={actor?.name}
              isStreaming
            />
          )}
        </div>

        {/* Voice controls or text input */}
        {!ended && isVoice && (
          <div className="flex flex-col items-center gap-2 border-t border-border px-4 py-6">
            <VoiceOrb state={voiceState} recording={recording} onToggle={toggleRecording} />
          </div>
        )}
        {!ended && !isVoice && <ChatInput onSend={sendMessage} disabled={isStreaming} />}
        {ended && (
          <div className="border-t border-border px-4 py-3 text-center text-sm text-muted-foreground">
            Session ended.{' '}
            <button
              onClick={() => navigate(`/results/${sessionId}`)}
              className="text-primary hover:underline"
            >
              View results →
            </button>
          </div>
        )}
      </div>

      {/* Right panel — coaching + trilemma (hidden on mobile) */}
      <div className="hidden lg:flex w-72 shrink-0 flex-col gap-4 border-l border-border pl-4 overflow-y-auto">
        <TrilemmaVisual state={trilemmaState} lastHorn={lastHorn} />
        <CoachingPanel annotations={annotations} />
      </div>
    </div>
  );
}
