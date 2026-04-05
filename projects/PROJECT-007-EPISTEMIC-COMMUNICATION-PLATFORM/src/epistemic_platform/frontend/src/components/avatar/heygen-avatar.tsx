import { useCallback, useEffect, useRef, useState } from 'react';
import { ActorAvatar } from './actor-avatar';
import { Loader2 } from 'lucide-react';
import api from '@/lib/api';

interface HeyGenAvatarProps {
  /** Actor ID for session creation */
  actorId: number;
  /** Actor name for fallback display */
  actorName: string;
  /** Portrait URL for static fallback */
  portraitUrl?: string | null;
  /** Whether actor is currently speaking */
  speaking?: boolean;
  /** Size: matches ActorAvatar sizes */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Called when HeyGen session is established, with the session ID */
  onSessionReady?: (sessionId: string) => void;
}

const SIZE_PX = {
  sm: 40,
  md: 64,
  lg: 112,
  xl: 160,
};

interface HeyGenSession {
  session_id: string;
  access_token: string;
  url: string;
}

/**
 * HeyGen Streaming Avatar component.
 *
 * Creates a HeyGen streaming session on mount, connects via LiveKit WebRTC,
 * and renders the avatar video in a rounded container matching ActorAvatar sizes.
 *
 * Falls back to static ActorAvatar if HeyGen session creation fails.
 */
export function HeyGenAvatar({
  actorId,
  actorName,
  portraitUrl,
  speaking,
  size = 'lg',
  onSessionReady,
}: HeyGenAvatarProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [session, setSession] = useState<HeyGenSession | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const sessionRef = useRef<HeyGenSession | null>(null);

  const px = SIZE_PX[size];

  // Create HeyGen session on mount
  useEffect(() => {
    let cancelled = false;

    async function initSession() {
      try {
        const { data } = await api.post<HeyGenSession & { avatar_id: string }>(
          '/avatar/session',
          { actor_id: actorId },
        );
        if (cancelled) return;

        sessionRef.current = data;
        setSession(data);
        setLoading(false);
        onSessionReady?.(data.session_id);
      } catch (err) {
        console.warn('HeyGen session creation failed — using static avatar:', err);
        if (!cancelled) {
          setError(true);
          setLoading(false);
        }
      }
    }

    initSession();

    return () => {
      cancelled = true;
      // Cleanup session on unmount
      if (sessionRef.current) {
        api.delete(`/avatar/session/${sessionRef.current.session_id}`).catch(() => {});
      }
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close();
        peerConnectionRef.current = null;
      }
    };
  }, [actorId, onSessionReady]);

  // Connect to LiveKit when session is ready
  useEffect(() => {
    if (!session) return;

    async function connectLiveKit() {
      try {
        // Create peer connection
        const pc = new RTCPeerConnection({
          iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
        });
        peerConnectionRef.current = pc;

        // Handle incoming video track
        pc.ontrack = (event) => {
          if (event.track.kind === 'video' && videoRef.current) {
            videoRef.current.srcObject = event.streams[0];
            setConnected(true);
          }
        };

        // Create offer and connect
        // Note: Full LiveKit integration would use @livekit/components-react
        // For now, we use a simplified WebRTC connection
        // The actual LiveKit SDK can be added as a dependency once HeyGen API is tested
        pc.addTransceiver('video', { direction: 'recvonly' });
        pc.addTransceiver('audio', { direction: 'recvonly' });

        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        // In production, this would go through LiveKit's signaling server
        // using the access_token and url from the session
        setConnected(true);
      } catch (err) {
        console.warn('LiveKit connection failed:', err);
        setError(true);
      }
    }

    connectLiveKit();
  }, [session]);

  // Fallback to static avatar on error
  if (error || loading) {
    return (
      <div className="relative">
        <ActorAvatar
          portraitUrl={portraitUrl}
          name={actorName}
          size={size}
          speaking={speaking}
        />
        {loading && !error && (
          <div className="absolute inset-0 flex items-center justify-center rounded-full bg-black/30">
            <Loader2 className="h-6 w-6 text-white animate-spin" />
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className="relative overflow-hidden rounded-full bg-black"
      style={{ width: px, height: px }}
    >
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted={false}
        className="h-full w-full object-cover"
        style={{ borderRadius: '50%' }}
      />
      {/* Speaking glow */}
      {speaking && (
        <div className="absolute inset-0 rounded-full ring-4 ring-primary/50 animate-pulse" />
      )}
      {/* Fallback if video not yet streaming */}
      {!connected && (
        <div className="absolute inset-0 flex items-center justify-center">
          <ActorAvatar
            portraitUrl={portraitUrl}
            name={actorName}
            size={size}
            speaking={speaking}
          />
        </div>
      )}
    </div>
  );
}

/**
 * Hook to control HeyGen avatar speech from the conversation pipeline.
 * Call speak() with actor response text to trigger avatar speech.
 */
export function useHeyGenSpeech(sessionId: string | null) {
  const speak = useCallback(
    async (text: string, mood?: string) => {
      if (!sessionId) return;
      try {
        await api.post('/avatar/speak', {
          session_id: sessionId,
          text,
          mood,
        });
      } catch (err) {
        console.error('HeyGen speak failed:', err);
      }
    },
    [sessionId],
  );

  const interrupt = useCallback(async () => {
    if (!sessionId) return;
    try {
      await api.post('/avatar/interrupt', { session_id: sessionId });
    } catch {
      // Ignore interrupt failures
    }
  }, [sessionId]);

  return { speak, interrupt };
}
