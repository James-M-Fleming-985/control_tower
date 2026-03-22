import { cn, formatTime } from '@/lib/utils';

interface ChatBubbleProps {
  role: 'user' | 'actor';
  content: string;
  timestamp?: string;
  isStreaming?: boolean;
  actorName?: string;
}

export function ChatBubble({ role, content, timestamp, isStreaming, actorName }: ChatBubbleProps) {
  const isUser = role === 'user';

  return (
    <div className={cn('flex gap-3', isUser ? 'justify-end' : 'justify-start')}>
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/20 text-xs font-bold text-primary">
          {actorName?.charAt(0) ?? 'A'}
        </div>
      )}
      <div className={cn('max-w-[75%] space-y-1')}>
        <div
          className={cn(
            'rounded-lg px-3 py-2 text-sm leading-relaxed',
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-card border border-card-border',
          )}
        >
          {content}
          {isStreaming && <span className="streaming-cursor" />}
        </div>
        {timestamp && (
          <span className="block text-[10px] text-muted-foreground">
            {formatTime(timestamp)}
          </span>
        )}
      </div>
      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-bold text-foreground">
          You
        </div>
      )}
    </div>
  );
}
