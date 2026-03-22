import { HORN_COLORS } from '@/lib/constants';
import type { TrilemmaState, HornDetection } from '@/types/api';

interface Props {
  state: TrilemmaState | null;
  lastHorn: HornDetection | null;
}

const HORN_LABELS: Record<string, string> = {
  regress: 'Infinite Regress',
  circularity: 'Circular Reasoning',
  dogmatism: 'Dogmatic Assertion',
  escaped: 'Escaped!',
  exploring: 'Exploring',
};

export function TrilemmaVisual({ state, lastHorn }: Props) {
  if (!state) return null;

  const horns = [
    { key: 'regress', angle: 270 },
    { key: 'circularity', angle: 30 },
    { key: 'dogmatism', angle: 150 },
  ] as const;

  const currentHorn = state.current_horn ?? lastHorn?.horn ?? 'exploring';
  const color = HORN_COLORS[currentHorn] ?? HORN_COLORS.exploring;

  return (
    <div className="space-y-2">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Münchhausen Trilemma
      </h3>

      {/* Triangle visualization */}
      <div className="relative mx-auto h-32 w-32">
        <svg viewBox="0 0 100 100" className="h-full w-full">
          {/* Triangle outline */}
          <polygon
            points="50,10 90,80 10,80"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            className="text-border"
          />
          {/* Horn vertices */}
          {horns.map(({ key, angle }) => {
            const rad = (angle * Math.PI) / 180;
            const cx = 50 + 40 * Math.cos(rad);
            const cy = 50 + 40 * Math.sin(rad);
            const isActive = currentHorn === key;
            const hornColor = HORN_COLORS[key];
            return (
              <circle
                key={key}
                cx={cx}
                cy={cy}
                r={isActive ? 8 : 5}
                fill={isActive ? hornColor : 'transparent'}
                stroke={hornColor}
                strokeWidth="2"
                className="transition-all duration-500"
              />
            );
          })}
          {/* Center dot */}
          <circle cx="50" cy="57" r="4" fill={color} className="animate-pulse" />
        </svg>
      </div>

      {/* Status */}
      <div className="text-center">
        <span className="text-xs font-medium" style={{ color }}>
          {HORN_LABELS[currentHorn] ?? currentHorn}
        </span>
        {lastHorn?.explanation && (
          <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{String(lastHorn.explanation)}</p>
        )}
      </div>

      {/* Turn depth */}
      {state.depth != null && state.depth > 0 && (
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Depth</span>
          <span>{String(state.depth)}</span>
        </div>
      )}
    </div>
  );
}
