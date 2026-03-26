import type { CoachingAnnotation } from '@/types/api';
import { Lightbulb, X } from 'lucide-react';
import { useState } from 'react';

interface Props {
  annotations: CoachingAnnotation[];
}

export function CoachingPanel({ annotations }: Props) {
  const [dismissed, setDismissed] = useState<Set<number>>(new Set());

  const visible = annotations.filter((_, i) => !dismissed.has(i));
  if (!visible.length) return null;

  return (
    <div className="flex flex-col flex-1 min-h-0 space-y-2">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
        <Lightbulb className="h-3 w-3" /> Coaching
      </h3>
      <div className="space-y-2 flex-1 min-h-0 overflow-y-auto">
        {annotations.map((ann, i) => {
          if (dismissed.has(i)) return null;
          return (
            <div
              key={i}
              className="relative rounded-md border border-primary/30 bg-primary/5 px-3 py-2 text-xs"
            >
              <button
                onClick={() => setDismissed((p) => new Set(p).add(i))}
                className="absolute top-1 right-1 text-muted-foreground hover:text-foreground"
              >
                <X className="h-3 w-3" />
              </button>
              {ann.what_happened && (
                <p className="text-foreground font-medium mb-1">{ann.what_happened}</p>
              )}
              {ann.why_it_matters && (
                <p className="text-muted-foreground leading-relaxed">{ann.why_it_matters}</p>
              )}
              {ann.what_to_try && (
                <p className="mt-1 text-foreground italic">💡 {ann.what_to_try}</p>
              )}
              {!ann.what_happened && ann.summary && (
                <p className="text-muted-foreground leading-relaxed">{ann.summary}</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
