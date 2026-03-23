import { useEffect, useState } from 'react';

interface HealthInfo {
  version: string;
  git_commit: string;
  deploy_timestamp: string;
}

export function Footer() {
  const [info, setInfo] = useState<HealthInfo | null>(null);

  useEffect(() => {
    fetch('/health')
      .then((r) => r.json())
      .then((data: HealthInfo) => setInfo(data))
      .catch(() => {});
  }, []);

  if (!info) return null;

  const ts = info.deploy_timestamp?.slice(0, 19).replace('T', ' ') ?? '';

  return (
    <footer className="border-t border-border px-4 py-2 text-center text-xs text-muted-foreground">
      Epistemic Platform v{info.version} ({info.git_commit}) | Deployed: {ts}
      {' · '}
      <a href="/health/db" target="_blank" rel="noopener noreferrer" className="hover:underline">
        DB Status
      </a>
    </footer>
  );
}
