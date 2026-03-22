import type { CoachingAnnotation } from '@/types/api';
import { Badge } from '@/components/ui/badge';
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
    <div className="space-y-2">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
        <Lightbulb className="h-3 w-3" /> Coaching
      </h3>
      <div className="space-y-2 max-h-60 overflow-y-auto">
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
              {ann.coaching_type && (
                <Badge variant="outline" className="mb-1 text-[10px]">
                  {String(ann.coaching_type)}
                </Badge>
              )}
              <p className="text-muted-foreground leading-relaxed">{String(ann.content)}</p>
              {ann.suggestion && (
                <p className="mt-1 text-foreground italic">💡 {String(ann.suggestion)}</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
