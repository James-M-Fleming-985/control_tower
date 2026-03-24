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
import { AudioWaveform } from '@/components/voice/audio-waveform';
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
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Voice-specific state
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [recording, setRecording] = useState(false);
  const [analyserNode, setAnalyserNode] = useState<AnalyserNode | null>(null);

  const wsRef = useRef<WebSocketManager | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Blob-based audio playback refs
  const audioChunksRef = useRef<ArrayBuffer[]>([]);
  const audioElRef = useRef<HTMLAudioElement | null>(null);
  const audioBlobUrlRef = useRef<string | null>(null);

  // Hands-free turn-taking refs
  const handsFreeRef = useRef(false);
  const silenceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const silenceCheckRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const recordingStartTimeRef = useRef<number>(0);
  const speechDetectedRef = useRef(false);
  const lastErrorTimeRef = useRef<number>(0);

  const SILENCE_THRESHOLD = 0.02; // RMS below this = silence
  const SPEECH_THRESHOLD = 0.03; // RMS above this = speech detected
  const SILENCE_DURATION_MS = 2000; // ms of silence after speech before auto-stop
  const MIN_RECORDING_MS = 2500; // minimum recording time before silence can trigger
  const GRACE_PERIOD_MS = 2000; // delay before silence detection kicks in
  const ERROR_COOLDOWN_MS = 3000; // don't auto-restart within this time after error

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

  // --- Audio playback helpers (Blob + <audio> element) ---
  const playAccumulatedAudio = useCallback(() => {
    if (audioChunksRef.current.length === 0) return;
    // Revoke previous URL if any
    if (audioBlobUrlRef.current) {
      URL.revokeObjectURL(audioBlobUrlRef.current);
      audioBlobUrlRef.current = null;
    }
    const blob = new Blob(audioChunksRef.current, { type: 'audio/mpeg' });
    audioChunksRef.current = [];
    const url = URL.createObjectURL(blob);
    audioBlobUrlRef.current = url;

    if (!audioElRef.current) {
      audioElRef.current = new Audio();
    }
    const audio = audioElRef.current;
    audio.src = url;
    audio.onended = () => {
      URL.revokeObjectURL(url);
      audioBlobUrlRef.current = null;
      setVoiceState('idle');
      // Auto-start mic for next turn — but only if no recent error
      if (handsFreeRef.current && Date.now() - lastErrorTimeRef.current > ERROR_COOLDOWN_MS) {
        startRecordingRef.current();
      }
    };
    audio.onerror = () => {
      console.error('Audio playback error');
      URL.revokeObjectURL(url);
      audioBlobUrlRef.current = null;
      setVoiceState('idle');
    };
    audio.play().catch((e) => console.error('Audio play() failed:', e));
  }, []);

  const enqueueAudio = useCallback((data: ArrayBuffer) => {
    audioChunksRef.current.push(data);
  }, []);

  const stopPlayback = useCallback(() => {
    audioChunksRef.current = [];
    if (audioElRef.current) {
      audioElRef.current.pause();
      audioElRef.current.src = '';
      audioElRef.current.onended = null;
    }
    if (audioBlobUrlRef.current) {
      URL.revokeObjectURL(audioBlobUrlRef.current);
      audioBlobUrlRef.current = null;
    }
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
          const backendState = data.state as string;
          if (backendState === 'listening') {
            setVoiceState('idle');
            // Don't auto-restart if we just had an error (prevents bounce loop)
          } else {
            setVoiceState(backendState as VoiceState);
          }
        }
        break;
      case 'audio_end':
        // All TTS chunks arrived — play the accumulated audio blob
        playAccumulatedAudio();
        break;
      case 'barge_in':
        stopPlayback();
        break;
      case 'session_ended':
        setEnded(true);
        break;
      case 'error':
        console.error('WS error:', (data as { detail: string }).detail);
        setErrorMsg((data as { detail: string }).detail);
        setIsStreaming(false);
        setStreamBuf('');
        setVoiceState('idle');
        lastErrorTimeRef.current = Date.now();
        setTimeout(() => setErrorMsg(null), 6000);
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
      micStreamRef.current?.getTracks().forEach((t) => t.stop());
      if (audioBlobUrlRef.current) URL.revokeObjectURL(audioBlobUrlRef.current);
      if (audioElRef.current) {
        audioElRef.current.pause();
        audioElRef.current.src = '';
      }
      if (silenceCheckRef.current) clearInterval(silenceCheckRef.current);
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    };
  }, []);

  // Auto-scroll
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, streamBuf]);

  // --- Recording controls with silence detection ---
  const stopSilenceDetection = useCallback(() => {
    if (silenceCheckRef.current) {
      clearInterval(silenceCheckRef.current);
      silenceCheckRef.current = null;
    }
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
  }, []);

  const stopRecording = useCallback(() => {
    stopSilenceDetection();
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    mediaRecorderRef.current = null;
    // Stop mic stream tracks
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach((t) => t.stop());
      micStreamRef.current = null;
    }
    setRecording(false);
    setAnalyserNode(null);
    if (wsRef.current) {
      wsRef.current.sendJSON({ type: 'end_utterance' });
    }
  }, [stopSilenceDetection]);

  const startRecording = useCallback(async () => {
    if (!wsRef.current || recording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = stream;

      // Set up AudioContext + AnalyserNode for silence detection & waveform
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }
      const ctx = audioContextRef.current;
      if (ctx.state === 'suspended') await ctx.resume();
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 2048;
      source.connect(analyser);
      setAnalyserNode(analyser);

      // Start MediaRecorder
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
      recorder.start(250);
      mediaRecorderRef.current = recorder;
      setRecording(true);
      setVoiceState('listening');
      handsFreeRef.current = true;
      recordingStartTimeRef.current = Date.now();
      speechDetectedRef.current = false;

      // --- Silence detection with grace period ---
      const dataArray = new Float32Array(analyser.fftSize);
      let silentSince: number | null = null;

      // Don't start silence detection until after the grace period
      silenceTimerRef.current = setTimeout(() => {
        silenceCheckRef.current = setInterval(() => {
          const elapsed = Date.now() - recordingStartTimeRef.current;
          analyser.getFloatTimeDomainData(dataArray);
          // Compute RMS
          let sum = 0;
          for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i] * dataArray[i];
          }
          const rms = Math.sqrt(sum / dataArray.length);

          // Track whether user has actually spoken
          if (rms >= SPEECH_THRESHOLD) {
            speechDetectedRef.current = true;
            silentSince = null;
          } else if (rms < SILENCE_THRESHOLD) {
            // Only start counting silence AFTER speech was detected AND min time passed
            if (speechDetectedRef.current && elapsed >= MIN_RECORDING_MS) {
              if (silentSince === null) silentSince = Date.now();
              if (Date.now() - silentSince >= SILENCE_DURATION_MS) {
                stopRecording();
              }
            }
          } else {
            // Between thresholds — ambiguous, reset silence counter
            silentSince = null;
          }
        }, 100);
      }, GRACE_PERIOD_MS);
    } catch (err) {
      console.error('Microphone access denied:', err);
    }
  }, [recording, stopRecording, SILENCE_THRESHOLD, SPEECH_THRESHOLD, SILENCE_DURATION_MS, MIN_RECORDING_MS, GRACE_PERIOD_MS]);

  // Stable ref so callbacks can access latest startRecording without re-renders
  const startRecordingRef = useRef(startRecording);
  startRecordingRef.current = startRecording;

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
            {isVoice && recording && (
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-green-500" />
              </span>
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
        {errorMsg && (
          <div className="mx-4 mt-2 rounded-md border border-destructive/50 bg-destructive/10 px-4 py-2 text-sm text-destructive">
            {errorMsg}
          </div>
        )}
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
          <div className="flex flex-col items-center gap-3 border-t border-border px-4 py-6">
            <VoiceOrb
              state={voiceState}
              recording={recording}
              onToggle={toggleRecording}
              actorName={actor?.name}
            />
            <AudioWaveform analyser={analyserNode} isActive={recording} />
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
