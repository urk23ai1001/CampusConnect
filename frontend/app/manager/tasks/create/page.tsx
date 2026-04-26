'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, usePathname } from 'next/navigation';
import { useAuth } from '../../../../context/AuthContext';

export default function TaskCreatePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [orgName, setOrgName] = useState<string>('');

  const searchParams = useSearchParams();
  const orgIdParam = searchParams.get('org_id');
  const orgId = orgIdParam ? parseInt(orgIdParam, 10) : null;

  const { user } = useAuth();

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [points, setPoints] = useState(0);
  const [deadline, setDeadline] = useState('');
  const [taskType, setTaskType] = useState('custom');

  // Fetch organization name on mount
  useEffect(() => {
    if (!orgId) return;
    const fetchOrgName = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/organizations/${orgId}`);
        if (!res.ok) {
          throw new Error('Failed to fetch organization');
        }
        const data = await res.json();
        setOrgName(data.name);
      } catch (err: any) {
        setError(err.message);
      }
    };
    fetchOrgName();
  }, [orgId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || user.role !== 'manager') {
      setError('Unauthorized');
      return;
    }
    if (!orgId) {
      setError('Organization ID is required');
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          org_id: orgId,
          title,
          description,
          points,
          deadline: deadline ? new Date(deadline).toISOString() : new Date().toISOString(),
          task_type: taskType,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to create task');
      }
      setSuccess('Task created successfully!');
      // Reset form
      setTitle('');
      setDescription('');
      setPoints(0);
      setDeadline('');
      setTaskType('custom');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!orgId) {
    return (
      <main className="min-h-screen flex flex-col justify-center items-center px-6 py-12 bg-slate-950">
        <h1 className="text-2xl font-bold text-center text-white">Error</h1>
        <p className="text-slate-400 text-center">Organization ID is required to create a task.</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white">Create Task</h1>
          <p className="text-slate-400 mt-2">For organization: {orgName || 'Loading...'}</p>
        </div>

        {error && <p className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded text-red-300">{error}</p>}
        {success && <p className="mb-4 p-3 bg-green-900/50 border border-green-700 rounded text-green-300">{success}</p>}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-slate-200 mb-1">
              Title
            </label>
            <input
              id="title"
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-900 text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-slate-200 mb-1">
              Description
            </label>
            <textarea
              id="description"
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-900 text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500 h-24 resize-y"
            />
          </div>

          <div className="grid gap-4 grid-cols-2">
            <div>
              <label htmlFor="points" className="block text-sm font-medium text-slate-200 mb-1">
                Points
              </label>
              <input
                id="points"
                type="number"
                min="0"
                required
                value={points}
                onChange={(e) => setPoints(parseInt(e.target.value) || 0)}
                className="w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-900 text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
            </div>

            <div>
              <label htmlFor="deadline" className="block text-sm font-medium text-slate-200 mb-1">
                Deadline
              </label>
              <input
                id="deadline"
                type="datetime-local"
                required
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                className="w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-900 text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
            </div>
          </div>

          <div>
            <label htmlFor="taskType" className="block text-sm font-medium text-slate-200 mb-1">
              Task Type
            </label>
            <select
              id="taskType"
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              className="w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-900 text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="referral">Referral</option>
              <option value="content">Content</option>
              <option value="promotion">Promotion</option>
              <option value="custom">Custom</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full px-4 py-2 bg-cyan-500 text-slate-950 font-semibold rounded-lg hover:bg-cyan-400 disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create Task'}
          </button>
        </form>
      </div>
    </main>
  );
}