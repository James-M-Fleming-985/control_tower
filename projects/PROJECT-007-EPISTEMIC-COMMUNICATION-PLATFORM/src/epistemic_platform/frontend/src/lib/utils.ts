import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDuration(startIso: string, endIso: string | null): string {
  if (!endIso) return 'In progress';
  const ms = new Date(endIso).getTime() - new Date(startIso).getTime();
  const mins = Math.round(ms / 60000);
  if (mins < 60) return `${mins}m`;
  return `${Math.floor(mins / 60)}h ${mins % 60}m`;
}

export function xpForLevel(level: number): number {
  if (level <= 1) return 0;
  return Math.round(100 * Math.pow(level - 1, 1.5));
}

export function xpProgress(xp: number, level: number): number {
  const current = xpForLevel(level);
  const next = xpForLevel(level + 1);
  if (next === current) return 100;
  return Math.round(((xp - current) / (next - current)) * 100);
}

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: 'bg-success/20 text-success',
  intermediate: 'bg-primary/20 text-primary-hover',
  advanced: 'bg-amber-500/20 text-amber-400',
  expert: 'bg-destructive/20 text-destructive',
};

export function difficultyClass(difficulty: string): string {
  return DIFFICULTY_COLORS[difficulty] ?? 'bg-muted text-muted-foreground';
}

const STANCE_LABELS: Record<string, string> = {
  foundationalist: 'Foundationalist',
  coherentist: 'Coherentist',
  pragmatist: 'Pragmatist',
  skeptic: 'Skeptic',
  empiricist: 'Empiricist',
  relativist: 'Relativist',
  infinitist: 'Infinitist',
  foundherentist: 'Foundherentist',
  virtue_epistemologist: 'Virtue Epistemologist',
  fallibilist: 'Fallibilist',
};

export function stanceLabel(stance: string): string {
  return STANCE_LABELS[stance] ?? stance.charAt(0).toUpperCase() + stance.slice(1);
}

const HORN_LABELS: Record<string, string> = {
  regress: 'Infinite Regress',
  circularity: 'Circularity',
  dogmatism: 'Dogmatism',
};

export function hornLabel(horn: string): string {
  return HORN_LABELS[horn] ?? horn;
}
