# PTE Preparation Platform — Living Spec

## Product
PTE Prep is a focused PTE Academic practice workspace for speaking, writing, reading, and listening. The MVP lets a learner choose a task, submit a text response, receive an estimated practice score and feedback, and see progress.

## MVP data model
- `PteTask`: task id, title, four-skill category, task type, difficulty, duration, prompt, instructions, and tags. The initial catalog contains original practice prompts, not Pearson question content.
- `Attempt`: task reference, skill, 10–90 estimated practice score, trait scores, feedback, answer preview, word count, timestamp, and `is_demo=true`.
- `DashboardSummary`: overall estimate, target score 79, streak, completed count, today's suggested count, skill scores, weakest area, and recent attempts.

## Key flows
1. Open dashboard and see target, estimated score, four skill cards, weak area, and task catalog.
2. Select a task from any skill card or task list.
3. Read the prompt, enter a response, and submit it.
4. See the estimated practice score, trait breakdown, feedback, and next-step action.
5. Return to the dashboard or open history to see the saved attempt.

## Scoring and integrations
The MVP uses a deterministic, realistic demo scoring engine on the backend. It is explicitly labelled as an estimated practice score and is not Pearson's official scoring engine. Live LLM scoring, speech-to-text, audio analysis, authentication, payments, and admin tooling are not enabled yet.

## Auth and roles
No authentication or role gates in the MVP. The app is a single learner demo workspace.