export type LeaderboardEntry = {
  rank: number;
  ambassador_id: number;
  ambassador_name: string;
  total_points: number;
  streak_count: number;
  badges: string[];
};

export type LeaderboardResponse = {
  entries: LeaderboardEntry[];
  updated_at: string;
};

export type Task = {
  id: number;
  org_id: number;
  title: string;
  description: string;
  points: number;
  deadline: string;
  task_type: string;
  created_by: number;
  created_at: string;
};

export type Submission = {
  id: number;
  task_id: number;
  ambassador_id: number;
  proof_url: string;
  status: string;
  score: number;
  created_at: string;
};
