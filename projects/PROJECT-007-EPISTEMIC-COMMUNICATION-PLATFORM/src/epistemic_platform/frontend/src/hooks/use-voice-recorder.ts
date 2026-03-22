import { useCallback, useRef, useState } from 'react';

export function useVoiceRecorder() {
  const [recording, setRecording] = useState(false);
  const mediaRecRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const onDataRef = useRef<((data: Blob) => void) | null>(null);

  const start = useCallback(async (onData: (chunk: Blob) => void) => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;

    const recorder = new MediaRecorder(stream, {
      mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm',
    });

    onDataRef.current = onData;

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) onDataRef.current?.(e.data);
    };

    recorder.start(250); // 250ms chunks
    mediaRecRef.current = recorder;
    setRecording(true);
  }, []);

  const stop = useCallback(() => {
    mediaRecRef.current?.stop();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    mediaRecRef.current = null;
    streamRef.current = null;
    setRecording(false);
  }, []);

  return { recording, start, stop };
}
