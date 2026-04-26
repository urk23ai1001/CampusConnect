'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '../../../../context/AuthContext';

export default function TaskSubmitPage() {
  const { taskId } = useParams();
  const { user } = useAuth();
  const router = useRouter();

  const [task, setTask] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [proofUrl, setProofUrl] = useState('');
  const [notes, setNotes] = useState('');

  // Fetch task details
  useEffect(() => {
    if (!taskId) return;
    const fetchTask = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/tasks/${taskId}`);
        if (!res.ok) {
          throw new Error('Failed to fetch task');
        }
        const data = await res.json();
        setTask(data);
      } catch (err: any) {
        setError(err.message);
      }
    };
    fetchTask();
  }, [taskId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || user.role !== 'ambassador') {
      setError('Unauthorized');
      return;
    }
    if (!taskId) {
      setError('Task ID is required');
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/submissions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_id: parseInt(taskId, 10),
          proof_url,
          notes: notes || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to submit');
      }
      setSuccess('Submission successful! Awaiting approval.');
      // Reset form
      setProofUrl('');
      setNotes('');
      // Optionally redirect to dashboard after a short delay
      setTimeout(() => {
        router.push('/ambassador/dashboard');
      }, 1500);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // If not authenticated as ambassador, redirect to login
  if (!user) {
    router.push('/auth/login');
    return null; // Prevent rendering while redirecting
  }
  if (user.role !== 'ambassador') {
    router.push('/manager/dashboard');
    return null;
  }

  if (!taskId) {
    return (
      <main className="min-h-screen flex flex-col justify-center items-center px-6 py-12 bg-slate-950">
        <h1 className="text-2xl font-bold text-center text-white">Error</h1>
        <p className="text-slate-400 text-center">Task ID is required.</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white">Submit Task Proof</h1>
          {task && (
            <div className="bg-slate-900/50 rounded-lg p-4 mb-6">
              <h2 className="text-xl font-semibold mb-2">{task.title}</h2>
              <p className="text-slate-400">{task.description}</p>
              <p className="text-slate-500 mt-2">Points: {task.points}</p>
            </div>
          )}
        </div>

        {error && <p className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded text-red-300">{error}</p>}
        {success && <p className="mb-4 p-3 bg-green-900/50 border border-green-700 rounded text-green-300">{success}</p>}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="proofUrl" className="block text-sm font-medium text-slate-200 mb-1">
              Proof URL (Image, Video, or Document Link)
            </label>
            <input
              id="proofUrl"
              type="url"
              required
              value={proofUrl}
              onChange={(e) => setProofUrl(e.target.value)}
              className="w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-900 text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              placeholder="Paste a link to your proof (e.g., Google Drive, Imgur, etc.)"
            />
          </div>

          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-slate-200 mb-1">
              Notes (Optional)
            </label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-900 text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500 h-24 resize-y"
              placeholder="Add any additional context or explanation"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full px-4 py-2 bg-cyan-500 text-slate-950 font-semibold rounded-lg hover:bg-cyan-400 disabled:opacity-50"
          >
            {loading ? 'Submitting...' : 'Submit Proof'}
          </button>
        </form>
      </div>
    </main>
  );
}