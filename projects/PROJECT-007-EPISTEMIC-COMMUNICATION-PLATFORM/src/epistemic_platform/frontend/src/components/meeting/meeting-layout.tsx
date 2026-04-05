import { useState, useRef, useEffect, type ReactNode } from 'react';
import { MessageSquare, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MeetingLayoutProps {
  /** Centre-stage content (avatar / orb / placeholder) */
  centerContent: ReactNode;
  /** Bottom toolbar buttons (mic, end, etc.) */
  toolbar: ReactNode;
  /** Chat transcript panel content */
  transcript: ReactNode;
  /** Optional right-side tabs (coaching, results, etc.) */
  sideTabs?: ReactNode;
  /** Status line below the centre content */
  statusText?: string;
  /** Header bar (back button, badges, etc.) */
  header?: ReactNode;
  /** Whether transcript panel is open by default */
  defaultTranscriptOpen?: boolean;
}

export function MeetingLayout({
  centerContent,
  toolbar,
  transcript,
  sideTabs,
  statusText,
  header,
  defaultTranscriptOpen = false,
}: MeetingLayoutProps) {
  const [transcriptOpen, setTranscriptOpen] = useState(defaultTranscriptOpen);
  const transcriptRef = useRef<HTMLDivElement>(null);

  // Auto-scroll transcript when open
  useEffect(() => {
    if (transcriptOpen && transcriptRef.current) {
      transcriptRef.current.scrollTo({ top: transcriptRef.current.scrollHeight, behavior: 'smooth' });
    }
  });

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Header */}
      {header && (
        <div className="flex items-center justify-between border-b border-border px-4 py-2 shrink-0">
          {header}
        </div>
      )}

      {/* Main area */}
      <div className="flex flex-1 min-h-0">
        {/* Centre stage */}
        <div className="flex flex-1 flex-col items-center justify-center min-w-0 relative">
          {/* Avatar / centre content */}
          <div className="flex flex-col items-center justify-center flex-1 w-full max-w-lg mx-auto px-4">
            {centerContent}
            {statusText && (
              <p className="mt-4 text-sm text-muted-foreground text-center animate-in fade-in">
                {statusText}
              </p>
            )}
          </div>

          {/* Bottom toolbar */}
          <div className="flex items-center justify-center gap-3 py-4 border-t border-border w-full shrink-0">
            {toolbar}
            <button
              onClick={() => setTranscriptOpen((o) => !o)}
              className={cn(
                'flex items-center gap-1.5 rounded-full px-3 py-2 text-xs transition-colors',
                transcriptOpen
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80',
              )}
              title={transcriptOpen ? 'Hide transcript' : 'Show transcript'}
            >
              <MessageSquare className="h-4 w-4" />
              <span className="hidden sm:inline">Chat</span>
            </button>
          </div>
        </div>

        {/* Transcript slide-out panel */}
        <div
          className={cn(
            'shrink-0 border-l border-border bg-card transition-all duration-300 overflow-hidden',
            transcriptOpen ? 'w-80 lg:w-96' : 'w-0',
          )}
        >
          {transcriptOpen && (
            <div className="flex h-full flex-col w-80 lg:w-96">
              {/* Panel header */}
              <div className="flex items-center justify-between border-b border-border px-3 py-2 shrink-0">
                <span className="text-sm font-medium">Transcript</span>
                <button
                  onClick={() => setTranscriptOpen(false)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              {/* Transcript messages */}
              <div ref={transcriptRef} className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
                {transcript}
              </div>
            </div>
          )}
        </div>

        {/* Optional side tabs (coaching, results) — hidden on mobile */}
        {sideTabs && (
          <div className="hidden lg:flex w-80 shrink-0 flex-col border-l border-border overflow-y-auto py-3 px-4">
            {sideTabs}
          </div>
        )}
      </div>
    </div>
  );
}
