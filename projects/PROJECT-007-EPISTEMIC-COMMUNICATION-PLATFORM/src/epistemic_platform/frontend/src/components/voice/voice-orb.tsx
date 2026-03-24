import { Mic, Loader2, Volume2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props {
  state: 'idle' | 'listening' | 'processing' | 'speaking';
  recording: boolean;
  onToggle: () => void;
  actorName?: string;
}

export function VoiceOrb({ state, recording, onToggle, actorName }: Props) {
  const isActive = state === 'listening' || recording;
  const isProcessing = state === 'processing';
  const isSpeaking = state === 'speaking';

  const label = (() => {
    if (isProcessing) return 'Processing...';
    if (isSpeaking) return `${actorName ?? 'Actor'} is speaking...`;
    if (isActive) return 'Listening...';
    return 'Tap to speak';
  })();

  return (
    <button
      onClick={onToggle}
      className={cn(
        'relative flex h-24 w-24 items-center justify-center rounded-full transition-all duration-300',
        isActive && 'bg-primary/20 ring-4 ring-primary/40 animate-pulse',
        isProcessing && 'bg-amber-500/20 ring-4 ring-amber-500/40',
        isSpeaking && 'bg-green-500/20 ring-4 ring-green-500/40',
        !isActive && !isProcessing && !isSpeaking && 'bg-muted hover:bg-muted/80',
      )}
      disabled={isProcessing || isSpeaking}
    >
      <div className={cn(
        'flex h-16 w-16 items-center justify-center rounded-full transition-colors',
        isActive && 'bg-primary',
        isProcessing && 'bg-amber-500',
        isSpeaking && 'bg-green-500',
        !isActive && !isProcessing && !isSpeaking && 'bg-card border border-border',
      )}>
        {isProcessing ? (
          <Loader2 className="h-6 w-6 text-white animate-spin" />
        ) : isSpeaking ? (
          <Volume2 className="h-6 w-6 text-white" />
        ) : (
          <Mic className={cn('h-6 w-6', isActive ? 'text-white' : 'text-muted-foreground')} />
        )}
      </div>

      {/* State label */}
      <span className="absolute -bottom-6 whitespace-nowrap text-xs text-muted-foreground">
        {label}
      </span>
    </button>
  );
}
