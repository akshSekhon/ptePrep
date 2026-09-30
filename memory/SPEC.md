# PTE Preparation Platform — Living Spec

## Product
PTE Prep is a focused PTE Academic practice workspace for speaking, writing, reading, and listening. Learners use saved test libraries: each individual practice type contains generated, imported, or guided 10-question tests, while skill modules can hold longer tests and full mocks are stored separately.

## Data model
- `PteTask`: id, title, explicit `task_type`, four-skill category, section, selected difficulty, duration, prompt, response mode, options, instructions, tags, optional chart data, and optional listening narration/transcript. The curated catalog covers 20 original task types and never uses Pearson question content.
- Each task also stores an `interaction_mode`, `scoring_mode`, and the applicable rubric traits. This ensures Read Aloud is recorded from visible text, Repeat Sentence/Retell Lecture play audio before recording, Describe Image shows data, and listening tasks play audio before response.
- `Attempt`: task reference, skill, selected difficulty, 10–90 estimated practice score, trait scores, feedback, answer preview, source, audio duration, timestamp, and whether a managed AI review was returned.
- `MockTest` and `MockResult`: a fresh 20-question level-based simulation, stored question order, aggregate section scores, and completion count.
- `ModuleTest` and `ModuleTestResult`: saved per-skill or per-task-type tests with 10–20 questions, level, voice preference, status, correct/wrong/unanswered counts, estimated score, and a retained list of revision mistakes. Learners can select multiple saved task tests and delete them with stored records and cached audio.
- `MockTest`: saved generated or imported full mocks with level and listening voice selection. A learner chooses Start explicitly; timers support start, pause, and resume rather than beginning on navigation.
- `TestSource`: a saved article, image, or audio file with topic metadata that can ground a new module test. Files are held in the test bank and served only when their test needs them.
- `StudyPlan`: four weekly action blocks ranked by weak-skill trend. `PricingPlan` exposes catalog-only module, section, and mock offers.

## Key flows
1. Open Practice, choose a task type such as Read Aloud, then select an existing test, generate a 10-question test, import JSON/CSV, or build 10–15 questions manually.
2. Optionally save an article, image, or audio source, then use its topic for a new original test; otherwise a current-topic-grounded test is generated and stored for reuse.
3. Before Speaking or Listening begins, a device-check page records a short microphone sample, lets the learner play it back, and runs a sound check. In-test recording uses explicit Start, Pause/Resume, and Stop controls; after Stop the learner can listen back, then choose “Use recording & transcribe” to unlock the next speaking question. Changing page stops all active microphone tracks, recorded playback, speech, and sound checks. Describe Image questions show an informative chart; Listening uses cached HD generated audio with native player progress/time and an optional transcript reveal; Speaking requires browser microphone access and Whisper transcription.
4. Complete a test to see correct, wrong, and unanswered counts; stored mistakes include the learner answer, revision cue, and explanation.
5. Use focused warm-ups, full mocks, study plan, history, or catalog as needed. Catalog buttons remain disabled because checkout is intentionally excluded.

## Scoring and integrations
Managed LLM reviews provide structured feedback when available, with a deterministic server-side fallback. Current-topic module tests use managed Gemini Flash with Google Search grounding and fall back to curated original topics; each generated test is stored in Mongo and reused until the learner explicitly asks for a different test. Listening audio uses cached `tts-1-hd` output through the managed integration; users may choose Australian or British practice varieties, while the provider cannot guarantee a regional accent. Browser audio uploads use managed Whisper transcription. AI reviews follow task-specific practice rules and return estimated—not official Pearson—scores. For spoken answers, pronunciation is estimated from transcription/audio signal and fluency from pace/phrasing; neither is a human or official acoustic confirmation. Authentication and checkout/payments are not enabled.

## Auth and roles
No authentication or role gates in the MVP. The app is a single learner demo workspace.