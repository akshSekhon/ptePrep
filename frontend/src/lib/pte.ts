export type Skill = "Speaking" | "Writing" | "Reading" | "Listening";

export interface PteTask {
  id: string;
  title: string;
  skill: Skill;
  task_type: string;
  difficulty: "Easy" | "Medium" | "Hard";
  duration_seconds: number;
  prompt: string;
  instructions: string;
  tags: string[];
}

export interface TraitScore {
  label: string;
  score: number;
  color: string;
}

export interface Attempt {
  id: string;
  task_id: string;
  task_title: string;
  skill: Skill;
  score: number;
  traits: TraitScore[];
  feedback: string[];
  answer_preview: string;
  word_count: number;
  created_at: string;
  is_demo: boolean;
}

export interface DashboardSummary {
  overall_score: number;
  target_score: number;
  streak_days: number;
  completed_tasks: number;
  today_tasks: number;
  skill_scores: Record<Skill, number>;
  weak_area: Skill;
  recent_attempts: Attempt[];
}

export interface AttemptCreate {
  task_id: string;
  answer_text: string;
}