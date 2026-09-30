import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from emergentintegrations.llm.openai.speech_to_text import OpenAISpeechToText
from lib.ai import generate_mock_prompts, review_answer
from lib.db import db
from models.pte import (
    Attempt,
    AttemptCreate,
    AudioTranscript,
    DashboardSummary,
    MockAnswer,
    MockCreate,
    MockQuestion,
    MockResult,
    MockSubmit,
    MockTest,
    PteTask,
    PricingPlan,
    StudyPlan,
    StudyPlanItem,
    TraitScore,
)

router = APIRouter(prefix="/pte", tags=["pte"])


RAW_TASKS: list[dict[str, Any]] = [
    {"id": "speaking-read-aloud-01", "title": "Read Aloud", "task_type": "Read Aloud", "skill": "Speaking", "section": "Speaking & Writing", "response_type": "audio", "prompt": "Technology has changed the way people communicate, work, and learn. While digital tools create new opportunities, thoughtful use is essential for maintaining meaningful human connection.", "instructions": "Read the passage clearly and naturally. Focus on steady pace, pronunciation, and complete word groups.", "tags": ["Pronunciation", "Oral fluency"]},
    {"id": "speaking-repeat-sentence-01", "title": "Repeat Sentence", "task_type": "Repeat Sentence", "skill": "Speaking", "section": "Speaking & Writing", "response_type": "audio", "prompt": "The university library will extend its opening hours during the examination period.", "instructions": "Listen once, then repeat the sentence with accurate content and natural rhythm.", "tags": ["Listening", "Oral fluency"]},
    {"id": "speaking-describe-image-01", "title": "Describe Image", "task_type": "Describe Image", "skill": "Speaking", "section": "Speaking & Writing", "response_type": "audio", "prompt": "Describe the relationship between steady daily practice and long-term exam performance. Mention the trend, a key comparison, and one conclusion.", "instructions": "Plan your response, then deliver a structured description with an opening, key details, and a conclusion.", "tags": ["Content", "Oral fluency"]},
    {"id": "speaking-retell-lecture-01", "title": "Retell Lecture", "task_type": "Retell Lecture", "skill": "Speaking", "section": "Speaking & Writing", "response_type": "audio", "prompt": "A strong study routine balances focused practice with deliberate rest. Short breaks protect attention, while weekly review helps learners notice patterns in their errors.", "instructions": "Retell the main idea and two supporting details in a connected response.", "tags": ["Content", "Fluency"]},
    {"id": "speaking-short-answer-01", "title": "Answer Short Question", "task_type": "Answer Short Question", "skill": "Speaking", "section": "Speaking & Writing", "response_type": "text", "prompt": "What do we call a place where books and other learning resources are kept?", "instructions": "Answer with a short, direct response.", "tags": ["Vocabulary", "Listening"]},
    {"id": "writing-summarize-text-01", "title": "Summarize Written Text", "task_type": "Summarize Written Text", "skill": "Writing", "section": "Speaking & Writing", "response_type": "text", "prompt": "Urban green spaces can reduce heat, support biodiversity, and improve mental wellbeing. However, they require thoughtful planning because poorly maintained parks may not serve the communities that need them most.", "instructions": "Write one sentence that captures the central idea and the important qualification.", "tags": ["Content", "Sentence structure"]},
    {"id": "writing-write-essay-01", "title": "Write Essay", "task_type": "Write Essay", "skill": "Writing", "section": "Speaking & Writing", "response_type": "text", "prompt": "Some people believe that technology makes life more complicated. Others think it makes life easier. Discuss both views and give your own opinion.", "instructions": "Write a clear essay with an introduction, developed arguments, examples, and a concise conclusion. Aim for 200–300 words.", "tags": ["Grammar", "Coherence"]},
    {"id": "reading-fib-dropdown-01", "title": "Fill in the Blanks — Dropdown", "task_type": "Reading & Writing: Fill in the Blanks", "skill": "Reading", "section": "Reading", "response_type": "choice", "options": ["effective", "temporary", "uncertain", "distant"], "prompt": "Regular study sessions are more ____ than last-minute revision because they give learners time to absorb information.", "instructions": "Choose the word that best completes the sentence.", "tags": ["Vocabulary", "Grammar"]},
    {"id": "reading-mc-multiple-01", "title": "Multiple Choice — Multiple Answers", "task_type": "Multiple Choice, Multiple Answer", "skill": "Reading", "section": "Reading", "response_type": "choice", "options": ["Review mistakes", "Avoid all feedback", "Set a specific goal", "Study without breaks"], "prompt": "Which two habits are most likely to support focused exam preparation?", "instructions": "Select the two best answers. Type them separated by a comma.", "tags": ["Comprehension", "Strategy"]},
    {"id": "reading-reorder-01", "title": "Reorder Paragraph", "task_type": "Re-order Paragraph", "skill": "Reading", "section": "Reading", "response_type": "text", "prompt": "Arrange these ideas into a logical paragraph: A. This makes feedback more useful. B. Learners improve faster when they review mistakes. C. It shows which strategy failed. D. Reflection turns an incorrect answer into a next step.", "instructions": "Type the best order using the letters, for example: B → C → A → D.", "tags": ["Logic", "Reading comprehension"]},
    {"id": "reading-fib-drag-01", "title": "Fill in the Blanks — Drag & Drop", "task_type": "Reading: Fill in the Blanks", "skill": "Reading", "section": "Reading", "response_type": "text", "prompt": "Good feedback is specific, timely, and ____; it should help a learner decide what to ____ next.", "instructions": "Complete the sentence with two suitable words.", "tags": ["Vocabulary", "Context"]},
    {"id": "reading-mc-single-01", "title": "Multiple Choice — Single Answer", "task_type": "Multiple Choice, Single Answer", "skill": "Reading", "section": "Reading", "response_type": "choice", "options": ["A weekly review", "A single late-night session", "Ignoring errors", "Changing goals daily"], "prompt": "Which approach best helps a learner notice progress over time?", "instructions": "Choose one answer.", "tags": ["Comprehension", "Strategy"]},
    {"id": "listening-summary-01", "title": "Summarize Spoken Text", "task_type": "Summarize Spoken Text", "skill": "Listening", "section": "Listening", "response_type": "text", "prompt": "A strong study routine balances focused practice with deliberate rest. Short breaks can protect attention, while weekly review helps learners notice patterns in their errors and adapt their plan.", "instructions": "Write a 50–70 word summary that includes the main idea and two supporting details.", "tags": ["Content", "Note-taking"]},
    {"id": "listening-mc-multiple-01", "title": "Multiple Choice — Multiple Answers", "task_type": "Multiple Choice, Multiple Answer", "skill": "Listening", "section": "Listening", "response_type": "choice", "options": ["Short breaks", "Weekly review", "No planning", "Skipping corrections"], "prompt": "Which two ideas support an effective study routine?", "instructions": "Select the two best answers separated by a comma.", "tags": ["Listening", "Comprehension"]},
    {"id": "listening-fib-01", "title": "Fill in the Blanks", "task_type": "Fill in the Blanks", "skill": "Listening", "section": "Listening", "response_type": "text", "prompt": "Consistent feedback helps students turn practice into measurable ____.", "instructions": "Type the missing word.", "tags": ["Listening", "Spelling"]},
    {"id": "listening-highlight-summary-01", "title": "Highlight Correct Summary", "task_type": "Highlight Correct Summary", "skill": "Listening", "section": "Listening", "response_type": "choice", "options": ["Practice is most useful when it is reviewed and adjusted.", "Practice should always be completed without breaks.", "Scores improve only through memorization.", "Feedback makes planning unnecessary."], "prompt": "Choose the summary that best captures the spoken passage about feedback and study routines.", "instructions": "Choose one answer.", "tags": ["Listening", "Main idea"]},
    {"id": "listening-mc-single-01", "title": "Multiple Choice — Single Answer", "task_type": "Multiple Choice, Single Answer", "skill": "Listening", "section": "Listening", "response_type": "choice", "options": ["Adapt a study plan", "Avoid all review", "Study only one skill", "Ignore timing"], "prompt": "What should a learner do after noticing a repeated error?", "instructions": "Choose one answer.", "tags": ["Listening", "Strategy"]},
    {"id": "listening-select-missing-01", "title": "Select Missing Word", "task_type": "Select Missing Word", "skill": "Listening", "section": "Listening", "response_type": "choice", "options": ["progress", "silence", "distance", "confusion"], "prompt": "Regular reflection turns practice into measurable ____.", "instructions": "Choose the word that completes the idea.", "tags": ["Vocabulary", "Context"]},
    {"id": "listening-highlight-incorrect-01", "title": "Highlight Incorrect Words", "task_type": "Highlight Incorrect Words", "skill": "Listening", "section": "Listening", "response_type": "text", "prompt": "Feedback helps learners identify patterns in their errors and adapt their study plan.", "instructions": "Type the words you believe should be corrected, separated by commas, or rewrite the sentence accurately.", "tags": ["Listening", "Accuracy"]},
    {"id": "listening-dictation-01", "title": "Write From Dictation", "task_type": "Write From Dictation", "skill": "Listening", "section": "Listening", "response_type": "text", "prompt": "Consistent feedback helps students turn practice into measurable progress.", "instructions": "Type the sentence as accurately as possible. Check spelling and word order.", "tags": ["Listening", "Spelling"]},
]


PRICING: list[PricingPlan] = [
    PricingPlan(id="skill-speaking", name="Speaking Module", scope="Single skill", price="$9", description="Focused practice for speaking tasks.", features=["All speaking task types", "AI practice reviews", "Audio transcription"], availability="catalog_only"),
    PricingPlan(id="skill-writing", name="Writing Module", scope="Single skill", price="$9", description="Build clearer, stronger written responses.", features=["Essay and summary tasks", "AI writing feedback", "Adaptive drills"], availability="catalog_only"),
    PricingPlan(id="section-pack", name="Full Section Pack", scope="One section", price="$19", description="A complete section-focused practice path.", features=["Level-based task sets", "Progress tracking", "Unlimited practice history"], availability="catalog_only"),
    PricingPlan(id="mock-pack", name="Mock Test Pack", scope="Full mock test", price="$29", description="Simulate the complete 20-type experience.", features=["Multiple generated mocks", "Timed transitions", "Combined result report"], availability="catalog_only"),
]


def _task(raw: dict[str, Any], level: str = "Medium") -> PteTask:
    copy = dict(raw)
    copy["difficulty"] = level
    copy.setdefault("duration_seconds", 60 if copy["skill"] == "Speaking" else 180)
    return PteTask(**copy)


def _normalise_datetime(doc: dict[str, Any]) -> dict[str, Any]:
    created_at = doc.get("created_at")
    if isinstance(created_at, datetime) and created_at.tzinfo is None:
        doc["created_at"] = created_at.replace(tzinfo=timezone.utc)
    return doc


def _fallback_review(task: PteTask, answer: str, source: str) -> tuple[int, list[TraitScore], list[str]]:
    words = len(answer.split())
    baseline = {"Speaking": 68, "Writing": 66, "Reading": 72, "Listening": 64}[task.skill]
    score = min(90, max(10, baseline + min(10, words // 20) + (4 if words >= 8 else 0)))
    labels = {"Speaking": ["Content", "Pronunciation", "Oral fluency"], "Writing": ["Content", "Grammar", "Vocabulary"], "Reading": ["Accuracy", "Vocabulary", "Comprehension"], "Listening": ["Accuracy", "Spelling", "Comprehension"]}[task.skill]
    traits = [TraitScore(label=label, score=min(90, max(10, score + shift)), color=color) for label, shift, color in zip(labels, [4, -2, 1], ["#0284c7", "#0d9488", "#d97706"])]
    feedback = ["You addressed the task with a clear central idea.", "Keep your response structured with purposeful transitions.", f"Next step: review {task.tags[0].lower()} before your next attempt."]
    if words < 8:
        feedback[0] = "Add more detail so your response fully develops the task."
    if source == "audio":
        feedback[1] = "Keep a steady pace and connect words smoothly between pauses."
    return score, traits, feedback


async def _review(task: PteTask, payload: AttemptCreate, answer: str) -> tuple[int, list[TraitScore], list[str], bool]:
    fallback = _fallback_review(task, answer, payload.source)
    try:
        result = await review_answer(task.model_dump(), answer, payload.difficulty, payload.audio_duration_seconds)
        score = min(90, max(10, int(result.get("score", fallback[0]))))
        raw_traits = result.get("traits", [])
        traits = [TraitScore(label=str(item.get("label", "Skill")), score=min(90, max(10, int(item.get("score", score)))), color=str(item.get("color", color))) for item, color in zip(raw_traits[:3], ["#0284c7", "#0d9488", "#d97706"])]
        if len(traits) != 3:
            return (*fallback, False)
        feedback = [str(item) for item in result.get("feedback", [])[:3]]
        if len(feedback) != 3:
            return (*fallback, False)
        return score, traits, feedback, True
    except Exception:
        return (*fallback, False)


@router.get("/tasks", response_model=list[PteTask])
async def get_tasks(level: str = "Medium") -> list[PteTask]:
    selected = level if level in {"Easy", "Medium", "Hard"} else "Medium"
    return [_task(item, selected) for item in RAW_TASKS]


@router.get("/tasks/{task_id}", response_model=PteTask)
async def get_task(task_id: str, level: str = "Medium") -> PteTask:
    raw = next((item for item in RAW_TASKS if item["id"] == task_id), None)
    if not raw:
        raise HTTPException(status_code=404, detail="Task not found")
    return _task(raw, level if level in {"Easy", "Medium", "Hard"} else "Medium")


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard() -> DashboardSummary:
    docs = await db.attempts.find().sort("created_at", -1).to_list(100)
    attempts = [Attempt(**_normalise_datetime(doc)) for doc in docs]
    scores = {"Speaking": 72, "Writing": 67, "Reading": 75, "Listening": 64}
    for attempt in attempts:
        scores[attempt.skill] = attempt.score
    return DashboardSummary(overall_score=round(sum(scores.values()) / 4), target_score=79, streak_days=12, completed_tasks=len(attempts), today_tasks=min(20, len(attempts) + 4), skill_scores=scores, weak_area=min(scores, key=scores.get), recent_attempts=attempts[:5])


@router.post("/attempts", response_model=Attempt)
async def create_attempt(payload: AttemptCreate) -> Attempt:
    raw = next((item for item in RAW_TASKS if item["id"] == payload.task_id), None)
    if not raw:
        raise HTTPException(status_code=404, detail="Task not found")
    task = _task(raw, payload.difficulty)
    score, traits, feedback, ai_feedback = await _review(task, payload, payload.answer_text)
    attempt = Attempt(task_id=task.id, task_title=task.title, skill=task.skill, difficulty=task.difficulty, score=score, traits=traits, feedback=feedback, answer_preview=payload.answer_text[:180], word_count=len(payload.answer_text.split()), source=payload.source, audio_duration_seconds=payload.audio_duration_seconds, is_demo=False, ai_feedback=ai_feedback)
    await db.attempts.insert_one(attempt.model_dump())
    return attempt


@router.get("/attempts", response_model=list[Attempt])
async def get_attempts() -> list[Attempt]:
    docs = await db.attempts.find().sort("created_at", -1).to_list(100)
    return [Attempt(**_normalise_datetime(doc)) for doc in docs]


@router.post("/transcribe", response_model=AudioTranscript)
async def transcribe_audio(file: UploadFile = File(...)) -> AudioTranscript:
    suffix = Path(file.filename or "response.webm").suffix.lower() or ".webm"
    if suffix.lstrip(".") not in {"webm", "wav", "mp3", "m4a", "mp4", "mpeg", "mpga"}:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    contents = await file.read()
    if not contents or len(contents) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Audio file must be between 1 byte and 25 MB")
    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(contents)
            temp_path = temp.name
        key = os.environ.get("EMERGENT_LLM_KEY")
        if not key:
            raise HTTPException(status_code=503, detail="Speech service is not configured")
        response = await OpenAISpeechToText(api_key=key).transcribe(temp_path, model="whisper-1", language="en")
        transcript = getattr(response, "text", None) or (response.get("text") if isinstance(response, dict) else None) or str(response)
        return AudioTranscript(transcript=transcript.strip(), language="en", provider="whisper-1")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Speech transcription unavailable: {exc}") from exc
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


@router.post("/mocks", response_model=MockTest)
async def create_mock(payload: MockCreate) -> MockTest:
    base_tasks = [_task(item, payload.level) for item in RAW_TASKS]
    generated_by_ai = False
    prompts: list[dict[str, str]] = []
    try:
        prompts = await generate_mock_prompts([item.model_dump() for item in base_tasks], payload.level)
        generated_by_ai = True
    except Exception:
        prompts = [{"prompt": item.prompt, "instructions": item.instructions} for item in base_tasks]
    questions: list[MockQuestion] = []
    for index, (task, generated) in enumerate(zip(base_tasks, prompts), start=1):
        data = task.model_dump()
        data.update(generated)
        data["order"] = index
        data["correct_answer"] = None
        questions.append(MockQuestion(**data))
    mock = MockTest(title=f"PTE Academic · {payload.level} mock", level=payload.level, questions=questions, total_time_seconds=sum(item.duration_seconds for item in questions), generated_by_ai=generated_by_ai)
    await db.mocks.insert_one(mock.model_dump())
    return mock


@router.post("/mocks/{mock_id}/submit", response_model=MockResult)
async def submit_mock(mock_id: str, payload: MockSubmit) -> MockResult:
    doc = await db.mocks.find_one({"id": mock_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Mock test not found")
    mock = MockTest(**_normalise_datetime(doc))
    answer_map = {answer.question_id: answer.answer.strip() for answer in payload.answers}
    section_values: dict[str, list[int]] = {}
    completed = 0
    for question in mock.questions:
        answer = answer_map.get(question.id, "")
        score = min(90, max(10, 58 + min(28, len(answer.split()) * 3))) if answer else 10
        if answer:
            completed += 1
        section_values.setdefault(question.section, []).append(score)
    section_scores = {section: round(sum(values) / len(values)) for section, values in section_values.items()}
    result = MockResult(mock_id=mock.id, title=mock.title, level=mock.level, overall_score=round(sum(section_scores.values()) / len(section_scores)), section_scores=section_scores, completed_count=completed, total_count=len(mock.questions))
    await db.mock_results.insert_one(result.model_dump())
    return result


@router.get("/study-plan", response_model=StudyPlan)
async def get_study_plan() -> StudyPlan:
    dashboard = await get_dashboard()
    ordered = sorted(dashboard.skill_scores.items(), key=lambda item: item[1])
    items = [StudyPlanItem(skill=skill, title=f"{skill} focus block", detail=f"Complete {4 if score < 70 else 2} targeted {skill.lower()} tasks and review every note.", task_count=4 if score < 70 else 2, priority="High" if index == 0 else ("Medium" if index < 3 else "Low")) for index, (skill, score) in enumerate(ordered)]
    return StudyPlan(title="Your adaptive 7-day plan", summary=f"Built from {dashboard.completed_tasks} completed reviews. Start with {dashboard.weak_area}, then keep the other skills moving.", based_on_attempts=dashboard.completed_tasks, items=items)


@router.get("/pricing", response_model=list[PricingPlan])
async def get_pricing() -> list[PricingPlan]:
    return PRICING