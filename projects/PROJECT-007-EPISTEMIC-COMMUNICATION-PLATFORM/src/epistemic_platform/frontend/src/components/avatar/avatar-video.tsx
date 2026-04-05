import { useCallback, useEffect, useRef, useState } from 'react';
import { ActorAvatar } from './actor-avatar';

interface AvatarVideoProps {
  /** WebSocket URL for the avatar service (e.g., wss://tunnel.example.com/ws/avatar/123) */
  avatarServiceUrl?: string | null;
  /** Actor name for init message and fallback */
  actorName: string;
  /** Portrait URL for static fallback */
  portraitUrl?: string | null;
  /** Whether TTS audio is currently playing — triggers lip-sync */
  isPlaying?: boolean;
  /** META tag data from the latest actor response */
  meta?: Record<string, string>;
  /** Audio data to send for lip-sync (raw ArrayBuffer chunks) */
  audioChunk?: ArrayBuffer | null;
  /** Size: matches ActorAvatar sizes */
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const SIZE_PX = {
  sm: 40,
  md: 64,
  lg: 112,
  xl: 160,
};

/**
 * Animated avatar component.
 *
 * When avatarServiceUrl is available, connects to the MuseTalk service via WebSocket,
 * sends audio chunks, and renders animated JPEG frames on a canvas.
 *
 * Falls back to static ActorAvatar (portrait or initials) when service is unavailable.
 */
export function AvatarVideo({
  avatarServiceUrl,
  actorName,
  portraitUrl,
  isPlaying,
  meta,
  audioChunk,
  size = 'lg',
}: AvatarVideoProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [hasFrames, setHasFrames] = useState(false);
  const frameQueueRef = useRef<Blob[]>([]);
  const animFrameRef = useRef<number>(0);
  const lastFrameTimeRef = useRef<number>(0);

  const px = SIZE_PX[size];

  // Connect to avatar service
  useEffect(() => {
    if (!avatarServiceUrl) return;

    const ws = new WebSocket(avatarServiceUrl);
    ws.binaryType = 'arraybuffer';
    wsRef.current = ws;

    ws.onopen = () => {
      // Send init with actor identity
      ws.send(
        JSON.stringify({
          type: 'init',
          actor_name: actorName,
          portrait_url: portraitUrl ?? '',
        }),
      );
    };

    ws.onmessage = (event) => {
      if (event.data instanceof ArrayBuffer) {
        // Binary: JPEG frame from MuseTalk
        frameQueueRef.current.push(new Blob([event.data], { type: 'image/jpeg' }));
        if (!hasFrames) setHasFrames(true);
      } else {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'ready') {
            setConnected(true);
          } else if (msg.type === 'error') {
            console.error('Avatar service error:', msg.detail);
          }
        } catch {
          // ignore
        }
      }
    };

    ws.onerror = () => {
      console.warn('Avatar service connection failed — using static avatar');
    };

    ws.onclose = () => {
      setConnected(false);
      wsRef.current = null;
    };

    return () => {
      ws.close();
      wsRef.current = null;
      setConnected(false);
    };
  }, [avatarServiceUrl, actorName, portraitUrl]);

  // Send META updates when expression changes
  useEffect(() => {
    if (!connected || !wsRef.current || !meta) return;
    wsRef.current.send(JSON.stringify({ type: 'meta', ...meta }));
  }, [connected, meta]);

  // Forward audio chunks to avatar service for lip-sync
  useEffect(() => {
    if (!connected || !wsRef.current || !audioChunk) return;
    wsRef.current.send(audioChunk);
  }, [connected, audioChunk]);

  // Send audio_end when playback stops
  useEffect(() => {
    if (!connected || !wsRef.current) return;
    if (!isPlaying) {
      wsRef.current.send(JSON.stringify({ type: 'audio_end' }));
    }
  }, [connected, isPlaying]);

  // Render frames from queue onto canvas
  const renderFrame = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const now = performance.now();
    const frameInterval = 1000 / 25; // 25 FPS

    if (now - lastFrameTimeRef.current >= frameInterval && frameQueueRef.current.length > 0) {
      const blob = frameQueueRef.current.shift()!;
      lastFrameTimeRef.current = now;

      const img = new Image();
      const url = URL.createObjectURL(blob);
      img.onload = () => {
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        }
        URL.revokeObjectURL(url);
      };
      img.src = url;
    }

    animFrameRef.current = requestAnimationFrame(renderFrame);
  }, []);

  useEffect(() => {
    if (hasFrames) {
      animFrameRef.current = requestAnimationFrame(renderFrame);
    }
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [hasFrames, renderFrame]);

  // If no avatar service or not connected, show static avatar
  if (!avatarServiceUrl || !connected) {
    return (
      <ActorAvatar
        portraitUrl={portraitUrl}
        name={actorName}
        size={size}
        speaking={isPlaying}
      />
    );
  }

  // Animated canvas — rendered as a circle to match avatar style
  return (
    <div
      className="relative rounded-full overflow-hidden border-2 border-border"
      style={{ width: px, height: px }}
    >
      <canvas
        ref={canvasRef}
        width={px * 2}
        height={px * 2}
        className="h-full w-full"
        style={{ imageRendering: 'auto' }}
      />
    </div>
  );
}
