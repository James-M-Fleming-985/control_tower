import { useState } from 'react';
import {
  useAvatarAssignments,
  useStockLibrary,
  useManualAssignAvatar,
  useRemoveAvatarAssignment,
  useReassignAllAvatars,
  type AvatarAssignment,
  type StockAvatar,
} from '@/hooks/use-api';
import {
  RefreshCw,
  Search,
  Trash2,
  Check,
  X,
  User,
  Loader2,
} from 'lucide-react';

export function AvatarLabPage() {
  const { data: assignments, isLoading } = useAvatarAssignments();
  const reassignAll = useReassignAllAvatars();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Avatar Lab</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage HeyGen avatar assignments for each actor
          </p>
        </div>
        <button
          onClick={() => reassignAll.mutate()}
          disabled={reassignAll.isPending}
          className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {reassignAll.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
          Re-assign All
        </button>
      </div>

      {/* Actor cards */}
      <div className="space-y-4">
        {assignments?.map((assignment) => (
          <ActorAvatarCard key={assignment.actor_id} assignment={assignment} />
        ))}
      </div>

      {!assignments?.length && (
        <div className="text-center py-12 text-muted-foreground">
          No actors found. Seed data may not have loaded.
        </div>
      )}
    </div>
  );
}

// ─── Actor Avatar Card ───────────────────────────────────────────────────────

function ActorAvatarCard({ assignment }: { assignment: AvatarAssignment }) {
  const [showBrowser, setShowBrowser] = useState(false);
  const removeAssignment = useRemoveAvatarAssignment();

  const hasAvatar = !!assignment.heygen_avatar_id;
  const statusBadge = !hasAvatar
    ? { label: 'No avatar', className: 'bg-muted text-muted-foreground' }
    : assignment.auto_assigned
      ? { label: 'Auto-assigned', className: 'bg-green-500/20 text-green-400' }
      : { label: 'Manual', className: 'bg-blue-500/20 text-blue-400' };

  return (
    <>
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="flex items-start gap-4">
          {/* Avatar preview */}
          <div className="h-20 w-20 shrink-0 rounded-lg bg-muted flex items-center justify-center overflow-hidden">
            {assignment.heygen_preview_url ? (
              <img
                src={assignment.heygen_preview_url}
                alt={assignment.heygen_avatar_name || 'Avatar'}
                className="h-full w-full object-cover"
              />
            ) : (
              <User className="h-8 w-8 text-muted-foreground" />
            )}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-foreground">{assignment.actor_name}</h3>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusBadge.className}`}>
                {statusBadge.label}
              </span>
            </div>
            {hasAvatar ? (
              <p className="text-sm text-muted-foreground mt-1">
                Avatar: <span className="text-foreground">{assignment.heygen_avatar_name}</span>
                <span className="text-xs ml-2 opacity-60">({assignment.heygen_avatar_id})</span>
              </p>
            ) : (
              <p className="text-sm text-muted-foreground mt-1">No avatar assigned — will use static portrait</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => setShowBrowser(true)}
              className="flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs font-medium hover:bg-accent transition-colors"
            >
              <Search className="h-3.5 w-3.5" />
              Browse Stock
            </button>
            {hasAvatar && (
              <button
                onClick={() => removeAssignment.mutate(assignment.actor_id)}
                disabled={removeAssignment.isPending}
                className="flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10 transition-colors disabled:opacity-50"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Remove
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stock browser modal */}
      {showBrowser && (
        <StockBrowserModal
          actorId={assignment.actor_id}
          actorName={assignment.actor_name}
          onClose={() => setShowBrowser(false)}
        />
      )}
    </>
  );
}

// ─── Stock Browser Modal ─────────────────────────────────────────────────────

function StockBrowserModal({
  actorId,
  actorName,
  onClose,
}: {
  actorId: number;
  actorName: string;
  onClose: () => void;
}) {
  const { data: avatars, isLoading, refetch, isFetched } = useStockLibrary();
  const assignAvatar = useManualAssignAvatar();
  const [genderFilter, setGenderFilter] = useState<string>('all');
  const [search, setSearch] = useState('');

  // Auto-fetch on mount
  if (!isFetched && !isLoading) {
    refetch();
  }

  const filtered = (avatars || []).filter((a) => {
    if (genderFilter !== 'all' && a.gender.toLowerCase() !== genderFilter) return false;
    if (search && !a.avatar_name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const handleSelect = (avatar: StockAvatar) => {
    assignAvatar.mutate(
      { actorId, avatarId: avatar.avatar_id },
      { onSuccess: () => onClose() },
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-card border border-border rounded-xl shadow-xl w-full max-w-3xl max-h-[80vh] flex flex-col m-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div>
            <h2 className="text-lg font-semibold">Browse Stock Avatars</h2>
            <p className="text-sm text-muted-foreground">
              Assigning to <span className="text-foreground font-medium">{actorName}</span>
            </p>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-accent">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 p-4 border-b border-border">
          <div className="flex items-center gap-1 rounded-md border border-border p-0.5">
            {['all', 'male', 'female'].map((g) => (
              <button
                key={g}
                onClick={() => setGenderFilter(g)}
                className={`rounded px-3 py-1 text-xs font-medium transition-colors ${
                  genderFilter === g
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent'
                }`}
              >
                {g.charAt(0).toUpperCase() + g.slice(1)}
              </button>
            ))}
          </div>
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-md border border-border bg-background pl-9 pr-3 py-1.5 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        </div>

        {/* Avatar grid */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-40">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No avatars match your filters
            </div>
          ) : (
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
              {filtered.map((avatar) => (
                <button
                  key={avatar.avatar_id}
                  onClick={() => handleSelect(avatar)}
                  disabled={assignAvatar.isPending}
                  className="group relative rounded-lg border border-border bg-muted/30 p-2 text-left hover:border-primary hover:bg-accent/50 transition-all disabled:opacity-50"
                >
                  <div className="aspect-square rounded-md bg-muted overflow-hidden mb-2">
                    {avatar.preview_image_url ? (
                      <img
                        src={avatar.preview_image_url}
                        alt={avatar.avatar_name}
                        className="h-full w-full object-cover"
                        loading="lazy"
                      />
                    ) : (
                      <div className="h-full w-full flex items-center justify-center">
                        <User className="h-8 w-8 text-muted-foreground" />
                      </div>
                    )}
                  </div>
                  <p className="text-xs font-medium truncate">{avatar.avatar_name}</p>
                  <p className="text-xs text-muted-foreground capitalize">{avatar.gender}</p>
                  {/* Hover overlay */}
                  <div className="absolute inset-0 rounded-lg flex items-center justify-center bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Check className="h-8 w-8 text-primary" />
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
