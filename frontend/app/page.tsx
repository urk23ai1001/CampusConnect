import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col justify-center items-center px-6 py-12 text-center">
      <div className="max-w-3xl w-full">
        <span className="inline-flex items-center px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-300 text-sm font-medium mb-6">
          Campus Ambassador platform
        </span>
        <h1 className="text-5xl font-semibold tracking-tight text-white mb-6">CampusConnect</h1>
        <p className="text-slate-300 text-lg leading-8 mb-8">
          Build, track, and reward campus ambassador programs with tasks, leaderboards, and real-time engagement.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link
            href="/dashboard"
            className="rounded-full bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 shadow hover:bg-cyan-400"
          >
            View dashboard
          </Link>
          <Link
            href="https://github.com"
            target="_blank"
            className="rounded-full border border-slate-700 px-6 py-3 text-sm font-semibold text-slate-200 hover:bg-slate-900"
          >
            Launch repo
          </Link>
        </div>
      </div>
    </main>
  );
}
