import dynamic from 'next/dynamic';

const Leaderboard = dynamic(() => import('../../components/Leaderboard'), { ssr: false });

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8">
          <p className="text-cyan-300 text-sm uppercase tracking-[0.32em] mb-2">CampusConnect</p>
          <h1 className="text-4xl font-semibold">Ambassador dashboard</h1>
          <p className="max-w-2xl text-slate-400 mt-3">
            Track tasks, submissions, and leaderboard movement for your ambassador program.
          </p>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
            <h2 className="text-2xl font-semibold mb-4">Live leaderboard</h2>
            <Leaderboard />
          </div>

          <div className="space-y-6">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
              <h2 className="text-2xl font-semibold mb-3">Quick actions</h2>
              <p className="text-slate-400 leading-7">
                Create tasks, review submissions, and award badges from the backend API.
              </p>
            </div>
            <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
              <h2 className="text-2xl font-semibold mb-3">Next steps</h2>
              <ul className="list-disc list-inside text-slate-400 leading-7">
                <li>Connect the React UI to auth and task endpoints.</li>
                <li>Wire ambassador submissions and manager review flows.</li>
                <li>Add badges, voting, and AI insights next.</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
