'use client';

import { useEffect, useState } from 'react';
import { fetcher } from '../lib/api';
import type { LeaderboardEntry, LeaderboardResponse } from '../lib/types';

export default function Leaderboard() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [updatedAt, setUpdatedAt] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadLeaderboard() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetcher<LeaderboardResponse>('/leaderboard?org_id=1');
        if (!isMounted) return;
        setEntries(data.entries);
        setUpdatedAt(new Date(data.updated_at).toLocaleTimeString());
      } catch (err) {
        if (!isMounted) return;
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadLeaderboard();
    const interval = setInterval(loadLeaderboard, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  if (loading) {
    return <p className="text-slate-400">Loading leaderboard…</p>;
  }

  if (error) {
    return <p className="text-rose-400">Failed to load leaderboard: {error}</p>;
  }

  if (entries.length === 0) {
    return <p className="text-slate-400">No leaderboard data yet. Approve submissions to populate the ranking.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-slate-400 text-sm">
        <span>Top ambassadors</span>
        <span>Updated at {updatedAt}</span>
      </div>
      <div className="divide-y divide-slate-800 rounded-3xl border border-slate-800 bg-slate-950/80 p-4">
        {entries.map((entry) => (
          <div key={entry.ambassador_id} className="flex items-center justify-between gap-4 py-4">
            <div>
              <p className="text-slate-300 text-sm">#{entry.rank} {entry.ambassador_name}</p>
              <p className="text-slate-500 text-xs">{entry.badges.length ? entry.badges.join(' • ') : 'No badges yet'}</p>
            </div>
            <div className="text-right">
              <p className="text-white font-semibold">{entry.total_points} pts</p>
              <p className="text-slate-500 text-xs">Streak {entry.streak_count}d</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
