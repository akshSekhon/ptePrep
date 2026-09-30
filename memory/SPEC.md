# PTE Preparation Platform — Living Spec

## Product
PTE Prep is a focused PTE Academic practice workspace for speaking, writing, reading, and listening. Learners open a skill module to complete a saved 20-question test, use browser-recorded speech for speaking, receive estimated feedback, and retain results plus revision mistakes.

## Data model
- `PteTask`: id, title, explicit `task_type`, four-skill category, section, selected difficulty, duration, prompt, response mode, options, instructions, tags, optional chart data, and optional listening narration/transcript. The curated catalog covers 20 original task types and never uses Pearson question content.
- `Attempt`: task reference, skill, selected difficulty, 10–90 estimated practice score, trait scores, feedback, answer preview, source, audio duration, timestamp, and whether a managed AI review was returned.
- `MockTest` and `MockResult`: a fresh 20-question level-based simulation, stored question order, aggregate section scores, and completion count.
- `ModuleTest` and `ModuleTestResult`: saved per-skill 20-question tests, a grounded or saved-source topic, correct/wrong/unanswered counts, estimated score, and a retained list of revision mistakes.
- `TestSource`: a saved article, image, or audio file with topic metadata that can ground a new module test. Files are held in the test bank and served only when their test needs them.
- `StudyPlan`: four weekly action blocks ranked by weak-skill trend. `PricingPlan` exposes catalog-only module, section, and mock offers.

## Key flows
1. Open the dashboard and choose a skill card to start or create a saved 20-question module test.
2. Optionally save an article, image, or audio source, then use its topic for a new original module test; otherwise a current-topic-grounded test is generated and stored for reuse.
3. Describe Image questions show an informative chart. Listening questions include browser audio playback with an optional transcript reveal. Speaking questions require browser microphone access and Whisper transcription—typed speaking answers are blocked.
4. Complete a test to see correct, wrong, and unanswered counts; stored mistakes include the learner answer, revision cue, and explanation.
5. Use focused warm-ups, full mocks, study plan, history, or catalog as needed. Catalog buttons remain disabled because checkout is intentionally excluded.

## Scoring and integrations
Managed LLM reviews provide structured feedback when available, with a deterministic server-side fallback. Current-topic module tests use managed Gemini Flash with Google Search grounding and fall back to curated original topics; each generated test is stored in Mongo and reused until the learner explicitly asks for a different test. Browser audio uploads use managed Whisper transcription. Describe Image feedback applies Content, Pronunciation, and Oral Fluency practice traits; pronunciation is estimated from the transcription/audio signal and is never represented as an official Pearson score or human confirmation. Authentication and checkout/payments are not enabled.

## Auth and roles
No authentication or role gates in the MVP. The app is a single learner demo workspace.