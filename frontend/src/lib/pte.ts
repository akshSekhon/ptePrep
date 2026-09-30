export type Skill = "Speaking" | "Writing" | "Reading" | "Listening";
export type Difficulty = "Easy" | "Medium" | "Hard";

export interface VisualData {
  type: "bar_chart" | "line_chart";
  title: string;
  x_label: string;
  y_label: string;
  labels: string[];
  values: number[];
  key_points: string[];
  image_url: string | null;
}

export interface PteTask {
  id: string;
  title: string;
  skill: Skill;
  section: string;
  task_type: string;
  difficulty: Difficulty;
  duration_seconds: number;
  prompt: string;
  instructions: string;
  response_type: "text" | "choice" | "audio";
  options: string[];
  tags: string[];
  visual: VisualData | null;
  listening_script: string | null;
  audio_url: string | null;
  source_topic: string | null;
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
  difficulty: Difficulty;
  score: number;
  traits: TraitScore[];
  feedback: string[];
  answer_preview: string;
  word_count: number;
  source: "text" | "audio";
  audio_duration_seconds: number | null;
  created_at: string;
  is_demo: boolean;
  ai_feedback: boolean;
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
  difficulty: Difficulty;
  source: "text" | "audio";
  audio_duration_seconds?: number;
}

export interface AudioTranscript {
  transcript: string;
  language: string;
  duration_seconds: number | null;
  provider: string;
}

export interface MockQuestion extends PteTask {
  order: number;
  correct_answer: string | null;
}

export interface MockTest {
  id: string;
  title: string;
  level: Difficulty;
  questions: MockQuestion[];
  total_time_seconds: number;
  created_at: string;
  generated_by_ai: boolean;
}

export interface MockAnswer {
  question_id: string;
  answer: string;
}

export interface MockResult {
  id: string;
  mock_id: string;
  title: string;
  level: Difficulty;
  overall_score: number;
  section_scores: Record<string, number>;
  completed_count: number;
  total_count: number;
  created_at: string;
}

export interface StudyPlanItem {
  skill: Skill;
  title: string;
  detail: string;
  task_count: number;
  priority: "High" | "Medium" | "Low";
}

export interface StudyPlan {
  title: string;
  summary: string;
  based_on_attempts: number;
  items: StudyPlanItem[];
}

export interface PricingPlan {
  id: string;
  name: string;
  scope: string;
  price: string;
  description: string;
  features: string[];
  availability: "included" | "catalog_only";
}

export interface ModuleTestCreate {
  skill: Skill;
  level: Difficulty;
  create_new: boolean;
  source_id?: string;
}

export interface ModuleQuestion extends PteTask {
  order: number;
}

export interface ModuleTest {
  id: string;
  title: string;
  skill: Skill;
  level: Difficulty;
  questions: ModuleQuestion[];
  total_time_seconds: number;
  topic: string;
  topic_source: "grounded" | "saved_source" | "curated";
  created_at: string;
}

export interface ModuleAnswer {
  question_id: string;
  answer: string;
}

export interface Mistake {
  question_id: string;
  task_title: string;
  task_type: string;
  learner_answer: string;
  correct_answer: string;
  explanation: string;
}

export interface ModuleTestResult {
  id: string;
  test_id: string;
  title: string;
  skill: Skill;
  correct_count: number;
  wrong_count: number;
  unanswered_count: number;
  total_count: number;
  estimated_score: number;
  mistakes: Mistake[];
  created_at: string;
}

export interface TestSource {
  id: string;
  title: string;
  kind: "article" | "image" | "audio";
  mime_type: string;
  topic: string;
  text_preview: string;
  created_at: string;
}