# PTE Preparation Platform — Living Spec

## Product
PTE Prep is a focused PTE Academic practice workspace for speaking, writing, reading, and listening. Learners select an original level-based task, submit a text response or browser-recorded speaking response, receive an estimated feedback review, and track progress.

## Data model
- `PteTask`: id, title, explicit `task_type`, four-skill category, section, selected difficulty, duration, prompt, response mode, options, instructions, and tags. The curated catalog covers 20 original task types and never uses Pearson question content.
- `Attempt`: task reference, skill, selected difficulty, 10–90 estimated practice score, trait scores, feedback, answer preview, source, audio duration, timestamp, and whether a managed AI review was returned.
- `MockTest` and `MockResult`: a fresh 20-question level-based simulation, stored question order, aggregate section scores, and completion count.
- `StudyPlan`: four weekly action blocks ranked by weak-skill trend. `PricingPlan` exposes catalog-only module, section, and mock offers.

## Key flows
1. Open the dashboard and see target, estimated score, four skill cards, weak area, adaptive plan, and task catalog.
2. Select a difficulty, then choose any curated task or start a newly generated full mock.
3. Read the prompt, type a response or record a speaking response in the browser; recorded audio is transcribed before submission.
4. Submit an answer for an estimated managed-AI review with deterministic fallback; results are saved and update progress.
5. Open the study plan, practice history, mock result, or pricing catalog. Catalog buttons remain disabled because checkout is intentionally excluded.

## Scoring and integrations
Managed LLM reviews provide structured feedback when available, with a deterministic server-side fallback so a learner is never blocked. Browser audio uploads use managed Whisper transcription. Mock prompts use managed generation with a curated fallback. All scores are estimated practice scores, never official Pearson scores. Authentication, checkout/payments, and admin tooling are not enabled.

## Auth and roles
No authentication or role gates in the MVP. The app is a single learner demo workspace.