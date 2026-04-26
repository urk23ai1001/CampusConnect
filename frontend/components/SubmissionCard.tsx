type SubmissionCardProps = {
  title: string;
  proofUrl: string;
  status: string;
  score: number;
};

export default function SubmissionCard({ title, proofUrl, status, score }: SubmissionCardProps) {
  return (
    <article className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <p className="text-slate-400 text-sm mt-2">Status: {status}</p>
        </div>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">Score: {score}</span>
      </div>
      <p className="mt-4 text-slate-500 text-sm">Proof: <a href={proofUrl} className="text-cyan-300 hover:text-cyan-200" target="_blank" rel="noreferrer">View submission</a></p>
    </article>
  );
}
