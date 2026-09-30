from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from lib.db import db
from models.pte import Attempt, AttemptCreate, DashboardSummary, PteTask, TraitScore

router = APIRouter(prefix="/pte", tags=["pte"])


TASKS: list[PteTask] = [
    PteTask(
        id="speaking-read-aloud-01",
        title="Read Aloud",
        skill="Speaking",
        task_type="Read Aloud",
        difficulty="Medium",
        duration_seconds=40,
        prompt="Technology has changed the way people communicate, work, and learn. While digital tools create new opportunities, thoughtful use is essential for maintaining meaningful human connection.",
        instructions="Read the passage clearly and naturally. Focus on steady pace, pronunciation, and complete word groups.",
        tags=["Pronunciation", "Oral fluency"],
    ),
    PteTask(
        id="speaking-describe-image-01",
        title="Describe Image",
        skill="Speaking",
        task_type="Describe Image",
        difficulty="Medium",
        duration_seconds=40,
        prompt="Describe the relationship between steady daily practice and long-term exam performance. Mention the trend, a key comparison, and one conclusion.",
        instructions="Plan your response, then deliver a structured description with an opening, key details, and a conclusion.",
        tags=["Content", "Oral fluency"],
    ),
    PteTask(
        id="writing-write-essay-01",
        title="Write Essay",
        skill="Writing",
        task_type="Write Essay",
        difficulty="Medium",
        duration_seconds=1200,
        prompt="Some people believe that technology makes life more complicated. Others think it makes life easier. Discuss both views and give your own opinion.",
        instructions="Write a clear essay with an introduction, developed arguments, examples, and a concise conclusion. Aim for 200–300 words.",
        tags=["Grammar", "Coherence"],
    ),
    PteTask(
        id="writing-summarize-text-01",
        title="Summarize Written Text",
        skill="Writing",
        task_type="Summarize Written Text",
        difficulty="Easy",
        duration_seconds=600,
        prompt="Urban green spaces can reduce heat, support biodiversity, and improve mental wellbeing. However, they require thoughtful planning because poorly maintained parks may not serve the communities that need them most.",
        instructions="Write one sentence that captures the central idea and the important qualification.",
        tags=["Content", "Sentence structure"],
    ),
    PteTask(
        id="reading-fill-blanks-01",
        title="Reading & Writing: Fill in the Blanks",
        skill="Reading",
        task_type="Fill in the Blanks",
        difficulty="Medium",
        duration_seconds=180,
        prompt="Researchers found that short, regular study sessions are more ____ than last-minute revision because they give learners time to ____ information and identify gaps in their knowledge.",
        instructions="Type the completed sentence using the best words for meaning and grammar. Suggested words: effective, absorb, postpone, repeat.",
        tags=["Vocabulary", "Grammar"],
    ),
    PteTask(
        id="reading-reorder-01",
        title="Reorder Paragraph",
        skill="Reading",
        task_type="Reorder Paragraph",
        difficulty="Hard",
        duration_seconds=150,
        prompt="Arrange these ideas into a logical paragraph: A. This makes feedback more useful. B. Learners improve faster when they review mistakes. C. It shows which strategy failed. D. Reflection turns an incorrect answer into a next step.",
        instructions="Type the best order using the letters, for example: B → C → A → D.",
        tags=["Logic", "Reading comprehension"],
    ),
    PteTask(
        id="listening-write-dictation-01",
        title="Write From Dictation",
        skill="Listening",
        task_type="Write From Dictation",
        difficulty="Medium",
        duration_seconds=90,
        prompt="Listen carefully to the sentence and type what you hear: Consistent feedback helps students turn practice into measurable progress.",
        instructions="Type the sentence as accurately as possible. Check spelling and word order before submitting.",
        tags=["Listening", "Spelling"],
    ),
    PteTask(
        id="listening-summary-01",
        title="Summarize Spoken Text",
        skill="Listening",
        task_type="Summarize Spoken Text",
        difficulty="Hard",
        duration_seconds=600,
        prompt="A strong study routine balances focused practice with deliberate rest. Short breaks can protect attention, while weekly review helps learners notice patterns in their errors and adapt their plan.",
        instructions="Write a 50–70 word summary that includes the main idea and two supporting details.",
        tags=["Content", "Note-taking"],
    ),
]


def _normalise_attempt(doc: dict) -> Attempt:
    created_at = doc.get("created_at")
    if isinstance(created_at, datetime) and created_at.tzinfo is None:
        doc["created_at"] = created_at.replace(tzinfo=timezone.utc)
    return Attempt(**doc)


def _score_for_answer(task: PteTask, answer: str) -> tuple[int, list[TraitScore], list[str]]:
    words = len(answer.split())
    length_bonus = min(10, max(0, words // 20))
    baseline = {"Speaking": 68, "Writing": 66, "Reading": 72, "Listening": 64}[task.skill]
    score = min(90, max(10, baseline + length_bonus + (4 if words >= 8 else 0)))
    colors = ["#0284c7", "#0d9488", "#d97706"]
    labels = {
        "Speaking": ["Content", "Pronunciation", "Oral fluency"],
        "Writing": ["Content", "Grammar", "Vocabulary"],
        "Reading": ["Accuracy", "Vocabulary", "Comprehension"],
        "Listening": ["Accuracy", "Spelling", "Comprehension"],
    }[task.skill]
    traits = [TraitScore(label=label, score=min(90, max(10, score + shift)), color=colors[index]) for index, (label, shift) in enumerate(zip(labels, [4, -2, 1]))]
    feedback = [
        "You addressed the task with a clear central idea.",
        "Keep your response structured with purposeful transitions.",
        "Next step: review the highlighted skill before your next attempt.",
    ]
    if words < 8:
        feedback[0] = "Add more detail so your response fully develops the task."
    return score, traits, feedback


@router.get("/tasks", response_model=list[PteTask])
async def get_tasks() -> list[PteTask]:
    return TASKS


@router.get("/tasks/{task_id}", response_model=PteTask)
async def get_task(task_id: str) -> PteTask:
    task = next((item for item in TASKS if item.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard() -> DashboardSummary:
    docs = await db.attempts.find().sort("created_at", -1).to_list(100)
    attempts = [_normalise_attempt(doc) for doc in docs]
    defaults = {"Speaking": 72, "Writing": 67, "Reading": 75, "Listening": 64}
    for attempt in attempts:
        defaults[attempt.skill] = attempt.score
    overall = round(sum(defaults.values()) / 4)
    weakest = min(defaults, key=defaults.get)
    return DashboardSummary(
        overall_score=overall,
        target_score=79,
        streak_days=12,
        completed_tasks=len(attempts),
        today_tasks=min(20, len(attempts) + 4),
        skill_scores=defaults,
        weak_area=weakest,
        recent_attempts=attempts[:5],
    )


@router.post("/attempts", response_model=Attempt)
async def create_attempt(payload: AttemptCreate) -> Attempt:
    task = next((item for item in TASKS if item.id == payload.task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    score, traits, feedback = _score_for_answer(task, payload.answer_text)
    attempt = Attempt(
        task_id=task.id,
        task_title=task.title,
        skill=task.skill,
        score=score,
        traits=traits,
        feedback=feedback,
        answer_preview=payload.answer_text[:180],
        word_count=len(payload.answer_text.split()),
    )
    await db.attempts.insert_one(attempt.model_dump())
    return attempt


@router.get("/attempts", response_model=list[Attempt])
async def get_attempts() -> list[Attempt]:
    docs = await db.attempts.find().sort("created_at", -1).to_list(100)
    return [_normalise_attempt(doc) for doc in docs]