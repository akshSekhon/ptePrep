import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  BrainCircuit,
  Check,
  ChevronRight,
  Clock3,
  Headphones,
  Flame,
  History,
  Info,
  LayoutDashboard,
  Mic2,
  PenLine,
  Play,
  RotateCcw,
  Send,
  Sparkles,
  Target,
  Trophy,
  Volume2,
} from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import type { Attempt, AttemptCreate, DashboardSummary, PteTask, Skill } from "@/lib/pte";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

type View = "overview" | "practice" | "history";

const skillMeta: Record<Skill, { icon: typeof Mic2; color: string; bg: string; copy: string }> = {
  Speaking: { icon: Mic2, color: "#0284c7", bg: "bg-sky-50", copy: "Build fluency & pronunciation" },
  Writing: { icon: PenLine, color: "#0d9488", bg: "bg-teal-50", copy: "Strengthen structure & grammar" },
  Reading: { icon: BookOpen, color: "#7c3aed", bg: "bg-violet-50", copy: "Sharpen speed & accuracy" },
  Listening: { icon: Headphones, color: "#d97706", bg: "bg-amber-50", copy: "Train focus & recall" },
};

const fetchDashboard = () => apiGet<DashboardSummary>("/pte/dashboard");
const fetchTasks = () => apiGet<PteTask[]>("/pte/tasks");
const fetchAttempts = () => apiGet<Attempt[]>("/pte/attempts");

function ScoreRing({ score, target }: { score: number; target: number }) {
  const progress = Math.max(0, Math.min(100, ((score - 10) / 80) * 100));
  return (
    <div className="relative flex h-44 w-44 items-center justify-center" data-testid="pte-overall-score-gauge">
      <div className="absolute inset-1 rounded-full bg-[conic-gradient(from_220deg,#0d9488_0%,#0284c7_65%,#e2e8f0_65%)] shadow-[0_18px_50px_rgba(2,132,199,0.18)]" style={{ background: `conic-gradient(from 220deg, #0d9488 0%, #0284c7 ${progress}%, #e2e8f0 ${progress}%)` }} />
      <div className="absolute inset-4 rounded-full bg-white" />
      <div className="relative text-center">
        <div className="font-mono text-5xl font-bold tracking-[-0.08em] text-slate-900" data-testid="overall-score-value">{score}</div>
        <div className="mt-1 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400" data-testid="overall-score-label">estimated overall</div>
      </div>
      <div className="absolute -bottom-1 rounded-full border border-sky-100 bg-white px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-sky-700 shadow-sm" data-testid="target-score-marker">Target {target}+</div>
    </div>
  );
}

function SkillCard({ skill, score, onPractice }: { skill: Skill; score: number; onPractice: () => void }) {
  const meta = skillMeta[skill];
  const Icon = meta.icon;
  return (
    <button type="button" onClick={onPractice} className="group rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition-[transform,box-shadow,border-color] duration-200 hover:-translate-y-1 hover:border-slate-300 hover:shadow-lg" data-testid={`skill-card-${skill.toLowerCase()}`}>
      <div className="flex items-start justify-between">
        <span className={`flex size-9 items-center justify-center rounded-lg ${meta.bg}`} style={{ color: meta.color }} data-testid={`${skill.toLowerCase()}-skill-icon`}><Icon size={18} /></span>
        <span className="font-mono text-2xl font-bold text-slate-900" data-testid={`${skill.toLowerCase()}-score`}>{score}</span>
      </div>
      <div className="mt-5 flex items-end justify-between gap-2">
        <div>
          <div className="text-sm font-bold text-slate-900" data-testid={`${skill.toLowerCase()}-skill-name`}>{skill}</div>
          <div className="mt-1 text-xs text-slate-500" data-testid={`${skill.toLowerCase()}-skill-copy`}>{meta.copy}</div>
        </div>
        <ChevronRight className="mb-1 text-slate-300 transition-transform duration-200 group-hover:translate-x-1" size={16} />
      </div>
      <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-slate-100" data-testid={`${skill.toLowerCase()}-score-progress`}><div className="h-full rounded-full" style={{ width: `${(score / 90) * 100}%`, backgroundColor: meta.color }} /></div>
    </button>
  );
}

function TaskCard({ task, onSelect }: { task: PteTask; onSelect: () => void }) {
  const meta = skillMeta[task.skill];
  const Icon = meta.icon;
  return (
    <div className="group flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-[transform,box-shadow] duration-200 hover:-translate-y-0.5 hover:shadow-md" data-testid={`task-card-${task.id}`}>
      <div>
        <div className="flex items-start justify-between gap-3">
          <span className="flex size-9 items-center justify-center rounded-lg bg-slate-50" style={{ color: meta.color }} data-testid={`${task.id}-icon`}><Icon size={17} /></span>
          <Badge variant="outline" data-testid={`${task.id}-difficulty`}>{task.difficulty}</Badge>
        </div>
        <div className="mt-5 text-base font-bold text-slate-900" data-testid={`${task.id}-title`}>{task.title}</div>
        <div className="mt-1 text-xs font-medium text-slate-500" data-testid={`${task.id}-skill`}>{task.skill} · {task.duration_seconds < 120 ? `${task.duration_seconds}s` : "Timed practice"}</div>
      </div>
      <Button className="mt-5 w-full" size="sm" onClick={onSelect} data-testid={`${task.id}-practice-button`}><Play size={14} fill="currentColor" /> Practice now</Button>
    </div>
  );
}

function FeedbackPanel({ attempt, onBack, onRetry }: { attempt: Attempt; onBack: () => void; onRetry: () => void }) {
  return (
    <div className="mx-auto max-w-5xl animate-rise space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div><div className="label-mono text-teal-700" data-testid="feedback-eyebrow">Practice review</div><h1 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-950" data-testid="feedback-title">Your practice snapshot</h1><p className="mt-2 text-sm text-slate-500" data-testid="feedback-subtitle">A clear next step is more useful than a perfect number.</p></div>
        <Badge className="border-teal-100 bg-teal-50 text-teal-700" variant="outline" data-testid="demo-score-badge"><Sparkles size={13} /> Demo AI estimate</Badge>
      </div>
      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.3fr]">
        <Card className="overflow-hidden border-0 bg-slate-950 text-white shadow-xl shadow-slate-900/10" data-testid="feedback-score-card">
          <CardContent className="relative p-7">
            <div className="absolute -right-12 -top-16 size-48 rounded-full bg-teal-400/20 blur-3xl" />
            <div className="relative"><div className="label-mono text-sky-300">Estimated PTE score</div><div className="mt-7 font-mono text-7xl font-bold tracking-[-0.1em]" data-testid="feedback-score-value">{attempt.score}</div><div className="mt-2 text-sm text-slate-300" data-testid="feedback-task-name">{attempt.task_title} · {attempt.skill}</div><div className="mt-8 h-px bg-white/10" /><div className="mt-5 flex items-center gap-2 text-xs text-slate-300" data-testid="feedback-disclaimer"><Info size={14} className="text-sky-300" /> Practice estimate, not an official Pearson score</div></div>
          </CardContent>
        </Card>
        <Card className="border-slate-200 shadow-sm" data-testid="feedback-traits-card">
          <CardHeader className="border-b border-slate-100"><CardTitle className="text-lg" data-testid="feedback-traits-title">Skill breakdown</CardTitle></CardHeader>
          <CardContent className="grid gap-5 p-6 sm:grid-cols-3">{attempt.traits.map((trait) => <div key={trait.label} data-testid={`feedback-trait-${trait.label.toLowerCase().replaceAll(" ", "-")}`}><div className="flex items-center justify-between text-sm"><span className="font-semibold text-slate-700">{trait.label}</span><span className="font-mono font-bold text-slate-950">{trait.score}</span></div><div className="mt-3 h-2 rounded-full bg-slate-100"><div className="h-full rounded-full" style={{ width: `${(trait.score / 90) * 100}%`, backgroundColor: trait.color }} /></div></div>)}</CardContent>
        </Card>
      </div>
      <div className="grid gap-6 lg:grid-cols-[1.3fr_0.9fr]">
        <Card className="border-slate-200 shadow-sm" data-testid="feedback-notes-card"><CardHeader><CardTitle className="text-lg" data-testid="feedback-notes-title">Coach notes</CardTitle></CardHeader><CardContent className="space-y-3">{attempt.feedback.map((note, index) => <div className="flex gap-3 rounded-lg bg-slate-50 p-4 text-sm leading-relaxed text-slate-600" key={note} data-testid={`feedback-note-${index + 1}`}><span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-teal-100 text-teal-700"><Check size={13} /></span><span>{note}</span></div>)}</CardContent></Card>
        <Card className="border-sky-100 bg-sky-50/60 shadow-sm" data-testid="next-step-card"><CardHeader><div className="flex size-9 items-center justify-center rounded-lg bg-white text-sky-600 shadow-sm"><Target size={18} /></div><CardTitle className="mt-3 text-lg" data-testid="next-step-title">Keep the momentum</CardTitle></CardHeader><CardContent><p className="text-sm leading-relaxed text-slate-600" data-testid="next-step-copy">Your next best move is one more {attempt.skill.toLowerCase()} task while the strategy is fresh.</p><Button className="mt-5 w-full" onClick={onRetry} data-testid="feedback-practice-again-button">Practice again <ArrowRight size={15} /></Button></CardContent></Card>
      </div>
      <Button variant="outline" onClick={onBack} data-testid="feedback-back-dashboard-button"><LayoutDashboard size={15} /> Back to dashboard</Button>
    </div>
  );
}

export default function Home() {
  const queryClient = useQueryClient();
  const [view, setView] = useState<View>("overview");
  const [selectedTask, setSelectedTask] = useState<PteTask | null>(null);
  const [answer, setAnswer] = useState("");
  const [submittedAttempt, setSubmittedAttempt] = useState<Attempt | null>(null);
  const dashboardQuery = useQuery({ queryKey: ["pte-dashboard"], queryFn: fetchDashboard, retry: false });
  const tasksQuery = useQuery({ queryKey: ["pte-tasks"], queryFn: fetchTasks, retry: false });
  const attemptsQuery = useQuery({ queryKey: ["pte-attempts"], queryFn: fetchAttempts, retry: false });
  const submitMutation = useMutation({
    mutationFn: (payload: AttemptCreate) => apiPost<Attempt>("/pte/attempts", payload),
    onSuccess: (attempt) => {
      setSubmittedAttempt(attempt);
      setAnswer("");
      queryClient.invalidateQueries({ queryKey: ["pte-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["pte-attempts"] });
      toast.success("Practice reviewed", { description: "Your estimated score and coach notes are ready." });
    },
    onError: () => toast.error("Could not submit", { description: "Please try again in a moment." }),
  });

  const dashboard = dashboardQuery.data;
  const tasks = tasksQuery.data ?? [];
  const groupedTasks = useMemo(() => tasks.reduce<Record<Skill, PteTask[]>>((groups, task) => { groups[task.skill].push(task); return groups; }, { Speaking: [], Writing: [], Reading: [], Listening: [] }), [tasks]);
  const openTask = (task: PteTask) => { setSelectedTask(task); setSubmittedAttempt(null); setAnswer(""); setView("practice"); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const closePractice = () => { setSelectedTask(null); setSubmittedAttempt(null); setView("overview"); };
  const nav = (nextView: View) => { setView(nextView); setSubmittedAttempt(null); if (nextView !== "practice") setSelectedTask(null); };

  return (
    <div className="min-h-svh bg-[#f8fafc] text-slate-900">
      <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl" data-testid="app-header">
        <div className="mx-auto flex h-[72px] max-w-[1440px] items-center justify-between px-4 sm:px-6 lg:px-8">
          <button type="button" className="flex items-center gap-3 text-left" onClick={() => nav("overview")} data-testid="brand-home-button"><span className="flex size-10 items-center justify-center rounded-xl bg-slate-950 text-white shadow-lg shadow-slate-900/15"><BrainCircuit size={21} /></span><span><span className="block font-heading text-base font-extrabold tracking-tight text-slate-950" data-testid="brand-name">PTE Prep</span><span className="block text-[10px] font-bold uppercase tracking-[0.2em] text-teal-600" data-testid="brand-tagline">Train with intent</span></span></button>
          <nav className="hidden items-center gap-1 rounded-xl bg-slate-50 p-1 md:flex" aria-label="Primary navigation" data-testid="primary-navigation">
            <button type="button" className={`nav-button ${view === "overview" ? "nav-button-active" : ""}`} onClick={() => nav("overview")} data-testid="nav-dashboard-button"><LayoutDashboard size={15} /> Dashboard</button>
            <button type="button" className={`nav-button ${view === "practice" ? "nav-button-active" : ""}`} onClick={() => { if (tasks[0]) openTask(tasks[0]); }} data-testid="nav-practice-button"><Play size={15} /> Practice</button>
            <button type="button" className={`nav-button ${view === "history" ? "nav-button-active" : ""}`} onClick={() => nav("history")} data-testid="nav-history-button"><History size={15} /> History</button>
          </nav>
          <div className="flex items-center gap-3"><div className="hidden items-center gap-2 rounded-full border border-amber-100 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-700 sm:flex" data-testid="streak-badge"><Flame size={14} /> {dashboard?.streak_days ?? 12} day streak</div><div className="flex size-9 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-800" data-testid="profile-avatar">AR</div></div>
        </div>
      </header>
      <div className="mx-auto flex max-w-[1440px]">
        <aside className="hidden w-60 shrink-0 border-r border-slate-200/80 px-5 py-8 lg:block" data-testid="desktop-sidebar"><div className="label-mono px-3 text-slate-400">Your workspace</div><div className="mt-4 space-y-1"><button type="button" className={`side-link ${view === "overview" ? "side-link-active" : ""}`} onClick={() => nav("overview")} data-testid="sidebar-dashboard-button"><LayoutDashboard size={16} /> Overview</button><button type="button" className={`side-link ${view === "practice" ? "side-link-active" : ""}`} onClick={() => { if (tasks[0]) openTask(tasks[0]); }} data-testid="sidebar-practice-button"><Target size={16} /> Practice center</button><button type="button" className={`side-link ${view === "history" ? "side-link-active" : ""}`} onClick={() => nav("history")} data-testid="sidebar-history-button"><BarChart3 size={16} /> Progress history</button></div><div className="mt-12 rounded-xl bg-slate-950 p-4 text-white"><div className="flex size-8 items-center justify-center rounded-lg bg-teal-400/20 text-teal-300"><Trophy size={16} /></div><div className="mt-4 text-sm font-bold" data-testid="sidebar-goal-title">Your goal</div><div className="mt-1 text-xs leading-relaxed text-slate-400" data-testid="sidebar-goal-copy">Build the habits that move you toward 79+.</div><div className="mt-4 h-1.5 rounded-full bg-white/10"><div className="h-full w-[72%] rounded-full bg-teal-400" /></div></div></aside>
        <main className="min-w-0 flex-1 px-4 py-7 sm:px-6 lg:px-10 lg:py-10">
          {view === "practice" && selectedTask && !submittedAttempt ? <PracticeView task={selectedTask} answer={answer} setAnswer={setAnswer} onSubmit={() => submitMutation.mutate({ task_id: selectedTask.id, answer_text: answer })} onBack={closePractice} isSubmitting={submitMutation.isPending} /> : null}
          {view === "practice" && submittedAttempt ? <FeedbackPanel attempt={submittedAttempt} onBack={closePractice} onRetry={() => selectedTask && openTask(selectedTask)} /> : null}
          {view === "history" ? <HistoryView attempts={attemptsQuery.data ?? []} onPractice={() => { if (tasks[0]) openTask(tasks[0]); }} /> : null}
          {view === "overview" ? <OverviewView dashboard={dashboard} tasks={tasks} groupedTasks={groupedTasks} onPractice={openTask} /> : null}
          {view === "practice" && !selectedTask ? <OverviewView dashboard={dashboard} tasks={tasks} groupedTasks={groupedTasks} onPractice={openTask} /> : null}
        </main>
      </div>
      <div className="fixed bottom-5 left-5 z-10 flex items-center gap-2 rounded-full border border-slate-200 bg-white/95 px-3 py-2 text-[11px] font-semibold text-slate-500 shadow-lg shadow-slate-900/5" data-testid="mocked-mode-indicator"><span className="size-1.5 rounded-full bg-amber-500" /> Demo scoring mode</div>
    </div>
  );
}

function OverviewView({ dashboard, tasks, groupedTasks, onPractice }: { dashboard?: DashboardSummary; tasks: PteTask[]; groupedTasks: Record<Skill, PteTask[]>; onPractice: (task: PteTask) => void }) {
  const firstTask = tasks[0];
  return <div className="mx-auto max-w-7xl animate-rise space-y-8"><section className="relative overflow-hidden rounded-2xl bg-slate-950 p-6 text-white shadow-xl shadow-slate-900/10 sm:p-8" data-testid="dashboard-hero"><div className="absolute -right-20 -top-32 size-80 rounded-full bg-sky-400/10 blur-3xl" /><div className="absolute bottom-0 right-1/4 h-40 w-40 rounded-full bg-teal-400/10 blur-3xl" /><div className="relative grid items-center gap-8 lg:grid-cols-[1fr_auto]"><div><div className="label-mono text-teal-300" data-testid="dashboard-eyebrow">Tuesday · your focus session</div><h1 className="mt-4 max-w-xl text-3xl font-extrabold tracking-[-0.04em] sm:text-4xl" data-testid="dashboard-heading">Make every practice minute count.</h1><p className="mt-4 max-w-lg text-sm leading-relaxed text-slate-300" data-testid="dashboard-intro">A focused path to your target score, with the right task waiting when you are ready.</p><div className="mt-7 flex flex-wrap gap-3"><Button className="bg-teal-400 text-slate-950 hover:bg-teal-300" onClick={() => firstTask && onPractice(firstTask)} data-testid="hero-start-practice-button"><Play size={15} fill="currentColor" /> Start practice</Button><div className="flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-300" data-testid="hero-today-plan"><Clock3 size={14} className="text-sky-300" /> {dashboard?.today_tasks ?? 4} tasks suggested today</div></div></div><div className="flex justify-center lg:pr-8"><ScoreRing score={dashboard?.overall_score ?? 69} target={dashboard?.target_score ?? 79} /></div></div></section><section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" data-testid="skill-score-grid">{(["Speaking", "Writing", "Reading", "Listening"] as Skill[]).map((skill) => <SkillCard key={skill} skill={skill} score={dashboard?.skill_scores[skill] ?? 0} onPractice={() => groupedTasks[skill][0] && onPractice(groupedTasks[skill][0])} />)}</section><section className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]"><div><div className="mb-4 flex items-end justify-between"><div><div className="label-mono text-slate-400" data-testid="task-section-eyebrow">Practice library</div><h2 className="mt-2 text-2xl font-extrabold tracking-tight text-slate-950" data-testid="task-section-title">Choose your next task</h2></div><button type="button" className="hidden items-center gap-1 text-xs font-bold text-sky-700 transition-colors hover:text-sky-900 sm:flex" data-testid="view-all-tasks-button">View all <ArrowRight size={14} /></button></div><div className="grid gap-4 sm:grid-cols-2">{tasks.slice(0, 4).map((task) => <TaskCard key={task.id} task={task} onSelect={() => onPractice(task)} />)}</div></div><Card className="self-start border-slate-200 shadow-sm" data-testid="weak-area-card"><CardHeader><div className="flex items-center justify-between"><div className="flex size-9 items-center justify-center rounded-lg bg-amber-50 text-amber-600"><Target size={17} /></div><Badge variant="outline" data-testid="weak-area-badge">Needs attention</Badge></div><CardTitle className="mt-4 text-lg" data-testid="weak-area-title">Strengthen your {dashboard?.weak_area ?? "Listening"}</CardTitle></CardHeader><CardContent><p className="text-sm leading-relaxed text-slate-500" data-testid="weak-area-copy">Small, specific sessions compound. Start with one task and use the feedback to choose the next.</p><Button variant="outline" className="mt-5 w-full" onClick={() => dashboard?.weak_area && groupedTasks[dashboard.weak_area][0] && onPractice(groupedTasks[dashboard.weak_area][0])} data-testid="weak-area-practice-button">Practice weak area <ArrowRight size={15} /></Button></CardContent></Card></section><section><div className="mb-4 flex items-end justify-between"><div><div className="label-mono text-slate-400" data-testid="skill-library-eyebrow">Explore by skill</div><h2 className="mt-2 text-2xl font-extrabold tracking-tight text-slate-950" data-testid="skill-library-title">A balanced score starts here</h2></div><div className="hidden items-center gap-2 text-xs text-slate-500 sm:flex" data-testid="catalog-count"><span className="size-1.5 rounded-full bg-teal-500" /> {tasks.length} original practice tasks</div></div><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{(["Speaking", "Writing", "Reading", "Listening"] as Skill[]).map((skill) => <div className="rounded-xl border border-slate-200 bg-white p-5" key={skill} data-testid={`library-card-${skill.toLowerCase()}`}><div className="flex items-center justify-between"><div className="flex items-center gap-2 text-sm font-bold text-slate-900"><span className="size-2 rounded-full" style={{ backgroundColor: skillMeta[skill].color }} /> {skill}</div><span className="font-mono text-xs text-slate-400">0{groupedTasks[skill].length}</span></div><div className="mt-4 space-y-2">{groupedTasks[skill].map((task) => <button type="button" key={task.id} className="flex w-full items-center justify-between rounded-lg bg-slate-50 px-3 py-2.5 text-left text-xs font-semibold text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900" onClick={() => onPractice(task)} data-testid={`library-task-${task.id}`}><span>{task.title}</span><ChevronRight size={14} className="text-slate-300" /></button>)}</div></div>)}</div></section></div>;
}

function PracticeView({ task, answer, setAnswer, onSubmit, onBack, isSubmitting }: { task: PteTask; answer: string; setAnswer: (value: string) => void; onSubmit: () => void; onBack: () => void; isSubmitting: boolean }) {
  const meta = skillMeta[task.skill];
  const isSpeaking = task.skill === "Speaking";
  return <div className="mx-auto max-w-5xl animate-rise space-y-6"><div className="flex flex-wrap items-center justify-between gap-4"><div><button type="button" className="mb-4 flex items-center gap-1 text-xs font-bold text-slate-500 transition-colors hover:text-slate-900" onClick={onBack} data-testid="practice-back-button"><ChevronRight size={14} className="rotate-180" /> Back to dashboard</button><div className="flex items-center gap-3"><span className="flex size-10 items-center justify-center rounded-xl bg-sky-50 text-sky-600"><Play size={18} fill="currentColor" /></span><div><div className="label-mono text-sky-700" data-testid="practice-eyebrow">{task.skill} practice · {task.task_type}</div><h1 className="mt-1 text-3xl font-extrabold tracking-tight text-slate-950" data-testid="practice-title">{task.title}</h1></div></div></div><div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600" data-testid="practice-timer"><Clock3 size={15} className="text-sky-600" /> {task.duration_seconds < 120 ? `${task.duration_seconds} sec response` : "Timed response"}</div></div><div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]"><Card className="border-slate-200 shadow-sm" data-testid="prompt-card"><CardHeader className="border-b border-slate-100"><div className="flex items-center justify-between"><div><div className="label-mono text-slate-400" data-testid="prompt-label">Prompt</div><CardTitle className="mt-2 text-xl" data-testid="prompt-title">Read the task carefully</CardTitle></div><Badge variant="outline" data-testid="prompt-difficulty">{task.difficulty}</Badge></div></CardHeader><CardContent className="p-6"><div className="rounded-xl bg-slate-50 p-5 text-base font-medium leading-8 text-slate-800" data-testid="task-prompt">{task.prompt}</div><div className="mt-5 flex gap-3 rounded-lg border border-sky-100 bg-sky-50/60 p-4 text-sm leading-relaxed text-slate-600" data-testid="task-instructions"><Info size={16} className="mt-0.5 shrink-0 text-sky-600" /> {task.instructions}</div>{isSpeaking && <div className="mt-5 rounded-xl border border-dashed border-teal-200 bg-teal-50/50 p-4" data-testid="speaking-simulation"><div className="flex items-center gap-3"><div className="flex size-9 items-center justify-center rounded-full bg-teal-100 text-teal-700"><Mic2 size={16} /></div><div><div className="text-sm font-bold text-slate-800">Speaking response</div><div className="text-xs text-slate-500">Type a response for this demo review. Audio scoring is coming next.</div></div><Volume2 size={18} className="ml-auto text-teal-500" /></div></div>}</CardContent></Card><Card className="border-slate-200 shadow-sm" data-testid="answer-card"><CardHeader><div className="label-mono text-slate-400" data-testid="answer-label">Your answer</div><CardTitle className="mt-2 text-xl" data-testid="answer-title">Show what you know</CardTitle></CardHeader><CardContent><Textarea value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder={isSpeaking ? "Type the response you would say aloud..." : "Write your response here..."} className="min-h-64 resize-y border-slate-200 bg-slate-50/60 p-4 leading-7 focus-visible:bg-white" data-testid="answer-textarea" /><div className="mt-3 flex items-center justify-between text-xs text-slate-400"><span data-testid="answer-word-count">{answer.trim() ? answer.trim().split(/\s+/).length : 0} words</span><span data-testid="answer-saving-note">Your response stays in this practice session</span></div><Button className="mt-6 w-full" disabled={!answer.trim() || isSubmitting} onClick={onSubmit} data-testid="submit-answer-button">{isSubmitting ? "Reviewing..." : "Submit for review"} {isSubmitting ? <Sparkles size={15} className="animate-pulse" /> : <Send size={15} />}</Button><div className="mt-4 flex items-center justify-center gap-2 text-[11px] text-slate-400" data-testid="practice-score-note"><Sparkles size={12} className="text-teal-500" /> Estimated practice feedback is generated in demo mode</div></CardContent></Card></div></div>;
}

function HistoryView({ attempts, onPractice }: { attempts: Attempt[]; onPractice: () => void }) {
  return <div className="mx-auto max-w-6xl animate-rise space-y-7"><div><div className="label-mono text-teal-700" data-testid="history-eyebrow">Your practice log</div><h1 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-950" data-testid="history-title">Progress history</h1><p className="mt-2 text-sm text-slate-500" data-testid="history-subtitle">Review the work you have completed and keep your next step visible.</p></div><Card className="border-slate-200 shadow-sm" data-testid="history-card"><CardHeader className="border-b border-slate-100"><div className="flex items-center justify-between"><CardTitle className="text-lg" data-testid="history-card-title">Completed practice</CardTitle><Badge variant="outline" data-testid="history-count-badge">{attempts.length} reviews</Badge></div></CardHeader><CardContent className="p-0">{attempts.length ? <div className="divide-y divide-slate-100">{attempts.map((attempt) => <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-5" key={attempt.id} data-testid={`history-row-${attempt.id}`}><div className="flex items-center gap-3"><span className="flex size-9 items-center justify-center rounded-lg bg-slate-50 text-sky-600"><Check size={16} /></span><div><div className="text-sm font-bold text-slate-900" data-testid={`history-task-${attempt.id}`}>{attempt.task_title}</div><div className="mt-1 text-xs text-slate-500">{attempt.skill} · {attempt.word_count} words · {new Date(attempt.created_at).toLocaleDateString()}</div></div></div><div className="flex items-center gap-5"><div className="text-right"><div className="font-mono text-xl font-bold text-slate-900" data-testid={`history-score-${attempt.id}`}>{attempt.score}</div><div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">estimate</div></div><ChevronRight size={16} className="text-slate-300" /></div></div>)}</div> : <div className="p-10 text-center"><History className="mx-auto text-slate-300" size={30} /><p className="mt-3 text-sm font-semibold text-slate-700" data-testid="history-empty-title">Your first review is waiting</p><p className="mt-1 text-xs text-slate-500" data-testid="history-empty-copy">Complete a practice task to start your progress log.</p><Button className="mt-5" onClick={onPractice} data-testid="history-start-practice-button">Start practice <ArrowRight size={15} /></Button></div>}</CardContent></Card><div className="flex items-center gap-3 rounded-xl border border-amber-100 bg-amber-50/60 p-4 text-xs leading-relaxed text-amber-800" data-testid="history-disclaimer"><Info size={15} className="shrink-0" /> Scores shown here are estimates for practice only. They are designed to guide your study habits, not predict an official result.</div></div>;
}
