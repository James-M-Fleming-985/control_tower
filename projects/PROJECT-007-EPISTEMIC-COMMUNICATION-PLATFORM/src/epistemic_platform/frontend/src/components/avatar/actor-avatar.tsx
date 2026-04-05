import { cn } from '@/lib/utils';

interface ActorAvatarProps {
  /** Portrait URL from actor.avatar_config?.portrait_url */
  portraitUrl?: string | null;
  /** Actor name for fallback initials */
  name: string;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Whether the actor is currently speaking (adds glow) */
  speaking?: boolean;
  /** Optional className override */
  className?: string;
}

const SIZE_CLASSES = {
  sm: 'h-10 w-10 text-sm',
  md: 'h-16 w-16 text-lg',
  lg: 'h-28 w-28 text-3xl',
  xl: 'h-40 w-40 text-5xl',
};

const RING_CLASSES = {
  sm: 'ring-2',
  md: 'ring-2',
  lg: 'ring-4',
  xl: 'ring-4',
};

function getInitials(name: string): string {
  return name
    .split(/\s+/)
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}

export function ActorAvatar({
  portraitUrl,
  name,
  size = 'lg',
  speaking = false,
  className,
}: ActorAvatarProps) {
  const sizeClass = SIZE_CLASSES[size];
  const ringClass = RING_CLASSES[size];

  return (
    <div
      className={cn(
        'relative flex items-center justify-center rounded-full overflow-hidden',
        'border-2 border-border bg-muted transition-all duration-300',
        speaking && `${ringClass} ring-green-400/60 animate-pulse`,
        sizeClass,
        className,
      )}
    >
      {portraitUrl ? (
        <img
          src={portraitUrl}
          alt={`${name} portrait`}
          className="h-full w-full object-cover"
          loading="lazy"
        />
      ) : (
        <span className="font-bold text-primary select-none">
          {getInitials(name)}
        </span>
      )}
    </div>
  );
}
