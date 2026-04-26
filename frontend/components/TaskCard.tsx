type TaskCardProps = {
  title: string;
  description: string;
  points: number;
  deadline: string;
};

export default function TaskCard({ title, description, points, deadline }: TaskCardProps) {
  return (
    <article className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <p className="text-slate-400 mt-2 text-sm leading-6">{description}</p>
        </div>
        <span className="rounded-full bg-cyan-500/10 text-cyan-300 px-3 py-1 text-xs font-semibold">{points} pts</span>
      </div>
      <div className="mt-4 text-slate-500 text-sm">Deadline: {new Date(deadline).toLocaleDateString()}</div>
    </article>
  );
}
