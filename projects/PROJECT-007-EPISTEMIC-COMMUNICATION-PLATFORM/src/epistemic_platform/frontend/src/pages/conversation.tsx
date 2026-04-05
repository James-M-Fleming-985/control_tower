import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useSession, useActor, useClientConfig } from '@/hooks/use-api';
import { useAuthStore } from '@/stores/auth-store';
import { WebSocketManager } from '@/lib/ws';
import { ChatBubble } from '@/components/conversation/chat-bubble';
import { ChatInput } from '@/components/conversation/chat-input';
import { CoachingPanel } from '@/components/conversation/coaching-panel';
import { TrilemmaVisual } from '@/components/conversation/trilemma-visual';
import { AudioWaveform } from '@/components/voice/audio-waveform';
import { MeetingLayout } from '@/components/meeting/meeting-layout';
import { ActorAvatar } from '@/components/avatar/actor-avatar';
import { HeyGenAvatar, useHeyGenSpeech } from '@/components/avatar/heygen-avatar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, Mic, StopCircle, Loader2, Volume2 } from 'lucide-react';
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
  const sessionReady = !!session;
  const { data: actor } = useActor(session?.actor_id ?? 0);
  const { data: clientConfig } = useClientConfig();
  const isVoice = session?.mode === 'voice';
  const isHeyGen = clientConfig?.avatar_mode === 'heygen' && clientConfig?.heygen_available;

  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [streamBuf, setStreamBuf] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [annotations, setAnnotations] = useState<CoachingAnnotation[]>([]);
  const [trilemmaState, setTrilemmaState] = useState<TrilemmaState | null>(null);
  const [lastHorn, setLastHorn] = useState<HornDetection | null>(null);
  const [lastStance, setLastStance] = useState<StanceDetection | null>(null);
  const [ended, setEnded] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [sessionReward, setSessionReward] = useState<Record<string, any> | null>(null);

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

  // Auto-start: track whether mic has been auto-launched
  const autoStartedRef = useRef(false);
  const [wsConnected, setWsConnected] = useState(false);

  // HeyGen avatar speech control
  const [heygenSessionId, setHeygenSessionId] = useState<string | null>(null);
  const { speak: heygenSpeak } = useHeyGenSpeech(heygenSessionId);

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
    if (audioChunksRef.current.length === 0) {
      console.warn('playAccumulatedAudio: no audio chunks to play');
      return;
    }
    // Check total byte size
    const totalBytes = audioChunksRef.current.reduce((sum, buf) => sum + buf.byteLength, 0);
    if (totalBytes < 100) {
      console.warn('playAccumulatedAudio: audio too small (%d bytes), skipping', totalBytes);
      audioChunksRef.current = [];
      return;
    }
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
      const code = audio.error?.code;
      const msg = audio.error?.message;
      console.error('Audio playback error:', { code, msg, blobSize: blob.size, chunks: audioChunksRef.current.length });
      URL.revokeObjectURL(url);
      audioBlobUrlRef.current = null;
      setVoiceState('idle');
    };
    audio.play().catch((e) => {
      console.error('Audio play() failed:', e);
      setErrorMsg('Audio playback blocked — tap the page and try again');
      setTimeout(() => setErrorMsg(null), 4000);
    });
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
      case 'heygen_speak':
        // HeyGen mode: backend skipped TTS, sends text for avatar to speak
        if ('text' in data && data.text) {
          setVoiceState('speaking');
          const mood = ('mood' in data ? (data.mood as string) : undefined);
          heygenSpeak(data.text as string, mood).then(() => {
            setVoiceState('idle');
            // Auto-restart mic for next turn
            if (handsFreeRef.current && Date.now() - lastErrorTimeRef.current > ERROR_COOLDOWN_MS) {
              startRecordingRef.current();
            }
          }).catch(() => {
            setVoiceState('idle');
          });
        }
        break;
      case 'barge_in':
        stopPlayback();
        break;
      case 'session_ended':
        // Stop reconnect IMMEDIATELY (synchronous) before React state update
        // to prevent race condition where server close arrives before cleanup effect
        wsRef.current?.stopReconnect();
        setEnded(true);
        if ('reward' in data && data.reward) {
          setSessionReward(data.reward as Record<string, unknown>);
        }
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
  }, [stopPlayback, heygenSpeak]);

  // --- Connect WebSocket ---
  // NOTE: Use `sessionReady` (boolean) instead of `session` (object) in deps
  // to prevent React Query refetches from tearing down the WebSocket mid-pipeline.
  useEffect(() => {
    if (!sessionId || !accessToken || ended || !sessionReady) return;

    const wsPath = isVoice
      ? `/ws/voice/${sessionId}`
      : `/ws/conversation/${sessionId}`;

    const ws = new WebSocketManager(wsPath, {
      onMessage: handleWsMessage,
      onBinary: isVoice ? enqueueAudio : undefined,
      onOpen: () => setWsConnected(true),
    });

    ws.connect();
    wsRef.current = ws;

    return () => {
      ws.close();
      wsRef.current = null;
      setWsConnected(false);
    };
  }, [sessionId, accessToken, ended, isVoice, sessionReady, handleWsMessage, enqueueAudio]);

  // Auto-start mic after WebSocket connects (voice mode only)
  useEffect(() => {
    if (!isVoice || !wsConnected || ended || autoStartedRef.current) return;
    autoStartedRef.current = true;
    // Brief delay so user sees "Connecting..." before mic activates
    const timer = setTimeout(() => {
      startRecordingRef.current();
    }, 1500);
    return () => clearTimeout(timer);
  }, [isVoice, wsConnected, ended]);

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
    const recorder = mediaRecorderRef.current;
    if (recorder?.state === 'recording') {
      // Wait for MediaRecorder to flush final audio chunk before signalling end.
      // onstop fires AFTER the last ondataavailable, so end_utterance arrives
      // at the backend after all audio data.
      recorder.onstop = () => {
        // Stop mic stream tracks
        if (micStreamRef.current) {
          micStreamRef.current.getTracks().forEach((t) => t.stop());
          micStreamRef.current = null;
        }
        // Small delay ensures the last ondataavailable's arrayBuffer().then()
        // resolves before we send end_utterance
        setTimeout(() => {
          if (wsRef.current) {
            wsRef.current.sendJSON({ type: 'end_utterance' });
          }
        }, 80);
      };
      recorder.stop();
    } else {
      // Recorder not active — just send end_utterance
      if (micStreamRef.current) {
        micStreamRef.current.getTracks().forEach((t) => t.stop());
        micStreamRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.sendJSON({ type: 'end_utterance' });
      }
    }
    mediaRecorderRef.current = null;
    setRecording(false);
    setAnalyserNode(null);
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

  // --- Shared elements ---
  const headerContent = (
    <>
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
          <Button size="sm" onClick={() => navigate(`/results/${sessionId}`, { state: { reward: sessionReward } })}>
            View Results
          </Button>
        )}
      </div>
    </>
  );

  const transcriptContent = (
    <>
      {errorMsg && (
        <div className="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {errorMsg}
        </div>
      )}
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
    </>
  );

  const endedBanner = ended && sessionReward?.score && (
    <div className="rounded-lg bg-primary/10 border border-primary/30 px-4 py-3 text-center space-y-1">
      <p className="text-lg font-bold text-primary">Session Complete!</p>
      <div className="flex items-center justify-center gap-4 text-sm">
        {sessionReward.score.grade && (
          <span className="font-semibold">Grade: {sessionReward.score.grade}</span>
        )}
        {sessionReward.score.final_score != null && (
          <span>Score: {Math.round(sessionReward.score.final_score)}/100</span>
        )}
        {sessionReward.xp_award?.total != null && (
          <span className="text-primary font-medium">+{sessionReward.xp_award.total} XP</span>
        )}
        {sessionReward.xp_award?.levelled_up && (
          <span className="font-bold text-amber-400">Level Up!</span>
        )}
      </div>
      {sessionReward.milestones?.newly_unlocked?.length > 0 && (
        <p className="text-xs text-muted-foreground">
          🏆 {sessionReward.milestones.newly_unlocked.length} new achievement{sessionReward.milestones.newly_unlocked.length > 1 ? 's' : ''} unlocked!
        </p>
      )}
    </div>
  );

  const sideTabsContent = (
    <>
      <TrilemmaVisual state={trilemmaState} lastHorn={lastHorn} />
      <CoachingPanel annotations={annotations} />
    </>
  );

  // --- Voice mode: Teams-style MeetingLayout ---
  if (isVoice) {
    const voiceStatusText = (() => {
      if (ended) return 'Session ended';
      if (voiceState === 'processing') return 'Processing…';
      if (voiceState === 'speaking') return `${actor?.name ?? 'Actor'} is speaking…`;
      if (recording) return 'Listening…';
      if (!wsConnected) return 'Connecting…';
      return 'Starting…';
    })();

    // Small state indicator icon (no button — mic auto-starts)
    const stateIndicator = (() => {
      if (ended || !wsConnected) return <Loader2 className="h-5 w-5 text-muted-foreground animate-spin" />;
      if (voiceState === 'processing') return <Loader2 className="h-5 w-5 text-amber-500 animate-spin" />;
      if (voiceState === 'speaking') return <Volume2 className="h-5 w-5 text-green-500" />;
      if (recording) return <Mic className="h-5 w-5 text-primary animate-pulse" />;
      return <Mic className="h-5 w-5 text-muted-foreground" />;
    })();

    return (
      <MeetingLayout
        header={headerContent}
        centerContent={
          <div className="flex flex-col items-center gap-4">
            {/* Actor avatar — HeyGen streaming or static */}
            {isHeyGen ? (
              <HeyGenAvatar
                actorId={session?.actor_id ?? 0}
                actorName={actor?.name ?? 'Actor'}
                portraitUrl={(actor?.avatar_config as Record<string, unknown>)?.portrait_url as string | undefined}
                speaking={voiceState === 'speaking'}
                size="lg"
                onSessionReady={setHeygenSessionId}
              />
            ) : (
              <ActorAvatar
                portraitUrl={(actor?.avatar_config as Record<string, unknown>)?.portrait_url as string | undefined}
                name={actor?.name ?? 'Actor'}
                size="lg"
                speaking={voiceState === 'speaking'}
              />
            )}
            <span className="text-sm font-medium">{actor?.name ?? 'Actor'}</span>
            {!ended && (
              <>
                {/* Subtle state indicator — no tap-to-talk button */}
                <div className="flex items-center gap-2">
                  {stateIndicator}
                  {recording && (
                    <span className="relative flex h-2 w-2">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75" />
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
                    </span>
                  )}
                </div>
                <AudioWaveform analyser={analyserNode} isActive={recording} />
              </>
            )}
            {endedBanner}
            {ended && (
              <div className="flex items-center gap-3 mt-2">
                <Button size="sm" onClick={() => navigate(`/results/${sessionId}`, { state: { reward: sessionReward } })}>
                  View Results
                </Button>
                <Button size="sm" variant="outline" onClick={() => navigate('/actors')}>
                  New Conversation
                </Button>
              </div>
            )}
          </div>
        }
        statusText={voiceStatusText}
        toolbar={
          <>
            {!ended && (
              <Button size="sm" variant="destructive" onClick={endSession}>
                <StopCircle className="mr-1 h-3 w-3" /> End
              </Button>
            )}
          </>
        }
        transcript={transcriptContent}
        sideTabs={sideTabsContent}
      />
    );
  }

  // --- Text mode: existing chat-first layout ---
  return (
    <div className="flex h-full gap-4">
      {/* Chat area */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header bar */}
        <div className="flex items-center justify-between border-b border-border px-4 py-2">
          {headerContent}
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

        {/* Text input or ended state */}
        {!ended && <ChatInput onSend={sendMessage} disabled={isStreaming} />}
        {ended && (
          <div className="border-t border-border px-4 py-4 space-y-3">
            {endedBanner}
            <div className="flex items-center justify-center gap-3">
              <Button
                size="sm"
                onClick={() => navigate(`/results/${sessionId}`, { state: { reward: sessionReward } })}
              >
                View Results
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => navigate('/actors')}
              >
                New Conversation
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Right panel — coaching + trilemma (hidden on mobile) */}
      <div className="hidden lg:flex w-72 shrink-0 flex-col gap-4 border-l border-border pl-4 overflow-hidden">
        {sideTabsContent}
      </div>
    </div>
  );
}
