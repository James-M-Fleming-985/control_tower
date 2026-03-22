import { cn } from '@/lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'destructive' | 'outline';
}

const variantClasses: Record<string, string> = {
  default: 'bg-primary/20 text-primary-hover',
  success: 'bg-success/15 text-success',
  warning: 'bg-amber-500/20 text-amber-400',
  destructive: 'bg-destructive/20 text-destructive',
  outline: 'border border-border text-muted-foreground',
};

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold uppercase tracking-wider',
        variantClasses[variant],
        className,
      )}
      {...props}
    />
  );
}
