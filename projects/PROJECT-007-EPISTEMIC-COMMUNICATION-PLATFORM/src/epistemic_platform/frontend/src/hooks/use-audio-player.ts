import { useRef, useCallback } from 'react';

export function useAudioPlayer() {
  const ctxRef = useRef<AudioContext | null>(null);
  const queueRef = useRef<AudioBuffer[]>([]);
  const playingRef = useRef(false);

  const getCtx = () => {
    if (!ctxRef.current) ctxRef.current = new AudioContext();
    return ctxRef.current;
  };

  const enqueue = useCallback(async (data: ArrayBuffer) => {
    const ctx = getCtx();
    const buf = await ctx.decodeAudioData(data.slice(0));
    queueRef.current.push(buf);
    if (!playingRef.current) playNext(ctx);
  }, []);

  const playNext = (ctx: AudioContext) => {
    const buf = queueRef.current.shift();
    if (!buf) {
      playingRef.current = false;
      return;
    }
    playingRef.current = true;
    const source = ctx.createBufferSource();
    source.buffer = buf;
    source.connect(ctx.destination);
    source.onended = () => playNext(ctx);
    source.start();
  };

  const stop = useCallback(() => {
    queueRef.current = [];
    playingRef.current = false;
    ctxRef.current?.close();
    ctxRef.current = null;
  }, []);

  return { enqueue, stop };
}
