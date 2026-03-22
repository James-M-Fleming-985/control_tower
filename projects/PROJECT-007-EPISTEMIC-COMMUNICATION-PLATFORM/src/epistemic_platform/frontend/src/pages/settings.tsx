import { useState } from 'react';
import { useAuthStore } from '@/stores/auth-store';
import { useUpdateProfile } from '@/hooks/use-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Settings as SettingsIcon, Check } from 'lucide-react';

export function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const updateProfile = useUpdateProfile();
  const [displayName, setDisplayName] = useState(user?.display_name ?? '');
  const [saved, setSaved] = useState(false);

  const save = async () => {
    const res = await updateProfile.mutateAsync({ display_name: displayName });
    updateUser(res);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (!user) return null;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-2">
        <SettingsIcon className="h-5 w-5 text-muted-foreground" />
        <h1 className="text-2xl font-bold">Settings</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Display Name</label>
            <Input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Your name"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Email</label>
            <Input value={user.email} disabled />
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={save} disabled={updateProfile.isPending || displayName === user.display_name}>
              {updateProfile.isPending ? 'Saving…' : 'Save Changes'}
            </Button>
            {saved && (
              <span className="flex items-center gap-1 text-sm text-green-400">
                <Check className="h-4 w-4" /> Saved
              </span>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Account</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Subscription</span>
            <Badge variant={user.subscription_tier === 'premium' ? 'default' : 'outline'}>
              {user.subscription_tier ?? 'free'}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Level</span>
            <span className="text-sm font-medium">{user.level}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Total XP</span>
            <span className="text-sm font-medium">{user.xp}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
