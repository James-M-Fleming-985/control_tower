import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/auth-store';
import { useSessionAnalysis, useSession, useActor } from '@/hooks/use-api';
import { WebSocketManager } from '@/lib/ws';
import { ChatBubble } from '@/components/conversation/chat-bubble';
import { ChatInput } from '@/components/conversation/chat-input';
import { VoiceOrb } from '@/components/voice/voice-orb';
import { AudioWaveform } from '@/components/voice/audio-waveform';
import { MeetingLayout } from '@/components/meeting/meeting-layout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { GraduationCap, ArrowLeft, Sparkles, Award, Target, MessageSquare, TrendingUp, Mic } from 'lucide-react';
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

type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking';

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

  // Voice state
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [recording, setRecording] = useState(false);
  const [analyserNode, setAnalyserNode] = useState<AnalyserNode | null>(null);

  const wsRef = useRef<WebSocketManager | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // TTS playback refs
  const audioChunksRef = useRef<ArrayBuffer[]>([]);
  const audioElRef = useRef<HTMLAudioElement | null>(null);
  const audioBlobUrlRef = useRef<string | null>(null);

  // Silence detection refs
  const silenceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const silenceCheckRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const recordingStartTimeRef = useRef<number>(0);
  const speechDetectedRef = useRef(false);

  const SILENCE_THRESHOLD = 0.02;
  const SPEECH_THRESHOLD = 0.03;
  const SILENCE_DURATION_MS = 2000;
  const MIN_RECORDING_MS = 2500;
  const GRACE_PERIOD_MS = 2000;

  // Fetch session data for right panel
  const { data: session } = useSession(Number(sessionId) || 0);
  const { data: actor } = useActor(session?.actor_id ?? 0);
  const isVoice = session?.mode === 'voice';
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

  // --- Audio playback helpers ---
  const playAccumulatedAudio = useCallback(() => {
    if (audioChunksRef.current.length === 0) return;
    const totalBytes = audioChunksRef.current.reduce((sum, buf) => sum + buf.byteLength, 0);
    if (totalBytes < 100) {
      audioChunksRef.current = [];
      return;
    }
    if (audioBlobUrlRef.current) {
      URL.revokeObjectURL(audioBlobUrlRef.current);
      audioBlobUrlRef.current = null;
    }
    const blob = new Blob(audioChunksRef.current, { type: 'audio/mpeg' });
    audioChunksRef.current = [];
    const url = URL.createObjectURL(blob);
    audioBlobUrlRef.current = url;

    if (!audioElRef.current) audioElRef.current = new Audio();
    const audio = audioElRef.current;
    audio.src = url;
    audio.onended = () => {
      URL.revokeObjectURL(url);
      audioBlobUrlRef.current = null;
      setVoiceState('idle');
    };
    audio.onerror = () => {
      URL.revokeObjectURL(url);
      audioBlobUrlRef.current = null;
      setVoiceState('idle');
    };
    setVoiceState('speaking');
    audio.play().catch(() => setVoiceState('idle'));
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
    setVoiceState('idle');
  }, []);

  // --- Recording controls ---
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
      recorder.onstop = () => {
        micStreamRef.current?.getTracks().forEach((t) => t.stop());
        micStreamRef.current = null;
        setTimeout(() => {
          wsRef.current?.sendJSON({ type: 'end_utterance' });
        }, 80);
      };
      recorder.stop();
    } else {
      micStreamRef.current?.getTracks().forEach((t) => t.stop());
      micStreamRef.current = null;
      wsRef.current?.sendJSON({ type: 'end_utterance' });
    }
    mediaRecorderRef.current = null;
    setRecording(false);
    setAnalyserNode(null);
    setVoiceState('processing');
  }, [stopSilenceDetection]);

  const startRecording = useCallback(async () => {
    if (!wsRef.current || recording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = stream;

      if (!audioContextRef.current) audioContextRef.current = new AudioContext();
      const ctx = audioContextRef.current;
      if (ctx.state === 'suspended') await ctx.resume();
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 2048;
      source.connect(analyser);
      setAnalyserNode(analyser);

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
      recordingStartTimeRef.current = Date.now();
      speechDetectedRef.current = false;

      // Silence detection with grace period
      const dataArray = new Float32Array(analyser.fftSize);
      let silentSince: number | null = null;

      silenceTimerRef.current = setTimeout(() => {
        silenceCheckRef.current = setInterval(() => {
          const elapsed = Date.now() - recordingStartTimeRef.current;
          analyser.getFloatTimeDomainData(dataArray);
          let sum = 0;
          for (let i = 0; i < dataArray.length; i++) sum += dataArray[i] * dataArray[i];
          const rms = Math.sqrt(sum / dataArray.length);

          if (rms >= SPEECH_THRESHOLD) {
            speechDetectedRef.current = true;
            silentSince = null;
          } else if (rms < SILENCE_THRESHOLD) {
            if (speechDetectedRef.current && elapsed >= MIN_RECORDING_MS) {
              if (silentSince === null) silentSince = Date.now();
              if (Date.now() - silentSince >= SILENCE_DURATION_MS) stopRecording();
            }
          } else {
            silentSince = null;
          }
        }, 100);
      }, GRACE_PERIOD_MS);
    } catch (err) {
      console.error('Microphone access denied:', err);
    }
  }, [recording, stopRecording, SILENCE_THRESHOLD, SPEECH_THRESHOLD, SILENCE_DURATION_MS, MIN_RECORDING_MS, GRACE_PERIOD_MS]);

  const toggleRecording = useCallback(() => {
    if (recording) stopRecording();
    else startRecording();
  }, [recording, startRecording, stopRecording]);

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

  useEffect(() => {
    if (!sessionId || !accessToken) return;

    const ws = new WebSocketManager(`/ws/debrief/${sessionId}?mode=${isVoice ? 'voice' : 'text'}`, {
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
          case 'transcription':
            if ('text' in data) {
              setMessages((prev) => [...prev, { role: 'user', content: data.text as string }]);
              setVoiceState('processing');
            }
            break;
          case 'audio_end':
            playAccumulatedAudio();
            break;
          case 'barge_in':
            stopPlayback();
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
      onBinary: isVoice ? enqueueAudio : undefined,
    });

    ws.connect();
    wsRef.current = ws;

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [sessionId, accessToken, isVoice, playAccumulatedAudio, stopPlayback, enqueueAudio]);

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

  // --- Shared sub-elements ---
  const headerLeft = (
    <div className="flex items-center gap-3">
      <button onClick={() => navigate('/dashboard')} className="text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" />
      </button>
      <Badge variant="default" className="gap-1">
        <GraduationCap className="h-3 w-3" /> Coach Debrief
      </Badge>
      {isVoice && (
        <Badge variant="outline" className="gap-1 text-xs">
          <Mic className="h-3 w-3" /> Voice
        </Badge>
      )}
      {actor && <span className="text-xs text-muted-foreground">Session with {actor.name}</span>}
    </div>
  );

  const transcriptContent = (
    <>
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
    </>
  );

  const resultsPanel = (
    <>
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
      {!score && !analysis && (
        <div className="text-center py-8">
          <Sparkles className="mx-auto h-6 w-6 text-muted-foreground/50 mb-2" />
          <p className="text-xs text-muted-foreground">Session results will appear here after the debrief</p>
        </div>
      )}
    </>
  );

  const endedButtons = (
    <div className="flex items-center justify-center gap-3">
      {readOnly && <span className="text-xs text-muted-foreground mr-2">Debrief Complete</span>}
      <Button size="sm" onClick={() => navigate('/dashboard')}>View Dashboard</Button>
      <Button size="sm" variant="outline" onClick={() => navigate('/actors')}>New Conversation</Button>
    </div>
  );

  // --- Voice mode: Teams-style MeetingLayout ---
  if (isVoice) {
    const voiceStatusText = (() => {
      if (ended || readOnly) return 'Debrief complete';
      if (voiceState === 'processing') return 'Processing…';
      if (voiceState === 'speaking') return 'Coach is speaking…';
      if (recording) return 'Listening…';
      return 'Tap the mic to respond';
    })();

    return (
      <MeetingLayout
        header={
          <>
            {headerLeft}
            {!ended && !readOnly && (
              <Button size="sm" variant="outline" onClick={endDebrief}>End Debrief</Button>
            )}
          </>
        }
        centerContent={
          <div className="flex flex-col items-center gap-4">
            <div className="flex h-28 w-28 items-center justify-center rounded-full bg-emerald-500/10 border-2 border-emerald-500/30">
              <GraduationCap className="h-12 w-12 text-emerald-500" />
            </div>
            <span className="text-sm font-medium">Coach</span>
            {!ended && !readOnly && (
              <>
                <VoiceOrb
                  state={voiceState}
                  recording={recording}
                  onToggle={toggleRecording}
                  actorName="Coach"
                />
                {analyserNode && recording && (
                  <AudioWaveform analyser={analyserNode} isActive={recording} />
                )}
              </>
            )}
            {(ended || readOnly) && endedButtons}
          </div>
        }
        statusText={voiceStatusText}
        toolbar={
          <>
            {!ended && !readOnly && (
              <Button size="sm" variant="outline" onClick={endDebrief}>End Debrief</Button>
            )}
          </>
        }
        transcript={transcriptContent}
        sideTabs={<div className="space-y-3">{resultsPanel}</div>}
        defaultTranscriptOpen={false}
      />
    );
  }

  // --- Text mode: existing two-column layout ---
  return (
    <div className="flex h-full gap-4">
      {/* Left column — chat */}
      <div className="flex flex-1 flex-col min-w-0">
        <div className="flex items-center justify-between border-b border-border px-4 py-2">
          {headerLeft}
          {!ended && (
            <Button size="sm" variant="outline" onClick={endDebrief}>End Debrief</Button>
          )}
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {transcriptContent}
        </div>

        {!ended && !readOnly ? (
          <ChatInput onSend={sendMessage} disabled={isStreaming} placeholder="Ask your coach about your session…" />
        ) : (
          <div className="border-t border-border px-4 py-3">
            {endedButtons}
          </div>
        )}
      </div>

      {/* Right panel — session results (hidden on mobile) */}
      <div className="hidden lg:flex w-80 shrink-0 flex-col gap-3 border-l border-border pl-4 overflow-y-auto py-3">
        {resultsPanel}
      </div>
    </div>
  );
}
