from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


Skill = Literal["Speaking", "Writing", "Reading", "Listening"]
Difficulty = Literal["Easy", "Medium", "Hard"]
ResponseType = Literal["text", "choice", "audio"]
SourceKind = Literal["article", "image", "audio"]
VoiceVariant = Literal["australian", "british"]


class VisualData(BaseModel):
    type: Literal["bar_chart", "line_chart"] = "bar_chart"
    title: str
    x_label: str
    y_label: str
    labels: list[str]
    values: list[int]
    key_points: list[str]
    image_url: str | None = None


class PteTask(BaseModel):
    id: str
    title: str
    skill: Skill
    section: str
    task_type: str
    difficulty: Difficulty
    duration_seconds: int
    prompt: str
    instructions: str
    response_type: ResponseType = "text"
    options: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    visual: VisualData | None = None
    listening_script: str | None = None
    audio_url: str | None = None
    source_topic: str | None = None


class TraitScore(BaseModel):
    label: str
    score: int
    color: str


class AttemptCreate(BaseModel):
    task_id: str
    answer_text: str = Field(min_length=1, max_length=12000)
    difficulty: Difficulty = "Medium"
    source: Literal["text", "audio"] = "text"
    audio_duration_seconds: int | None = None


class Attempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    task_title: str
    skill: Skill
    difficulty: Difficulty = "Medium"
    score: int
    traits: list[TraitScore]
    feedback: list[str]
    answer_preview: str
    word_count: int
    source: Literal["text", "audio"] = "text"
    audio_duration_seconds: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_demo: bool = False
    ai_feedback: bool = False


class DashboardSummary(BaseModel):
    overall_score: int
    target_score: int
    streak_days: int
    completed_tasks: int
    today_tasks: int
    skill_scores: dict[str, int]
    weak_area: str
    recent_attempts: list[Attempt]


class MockCreate(BaseModel):
    level: Difficulty = "Medium"
    voice: VoiceVariant = "australian"


class MockQuestion(PteTask):
    order: int
    correct_answer: str | None = None


class MockTest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    level: Difficulty
    questions: list[MockQuestion]
    total_time_seconds: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_by_ai: bool = False
    voice: VoiceVariant = "australian"


class MockAnswer(BaseModel):
    question_id: str
    answer: str = ""


class MockSubmit(BaseModel):
    answers: list[MockAnswer]


class MockResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    mock_id: str
    title: str
    level: Difficulty
    overall_score: int
    section_scores: dict[str, int]
    completed_count: int
    total_count: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StudyPlanItem(BaseModel):
    skill: Skill
    title: str
    detail: str
    task_count: int
    priority: Literal["High", "Medium", "Low"]


class StudyPlan(BaseModel):
    title: str
    summary: str
    based_on_attempts: int
    items: list[StudyPlanItem]


class PricingPlan(BaseModel):
    id: str
    name: str
    scope: str
    price: str
    description: str
    features: list[str]
    availability: Literal["included", "catalog_only"]


class AudioTranscript(BaseModel):
    transcript: str
    language: str
    duration_seconds: int | None = None
    provider: str


class ModuleTestCreate(BaseModel):
    skill: Skill
    level: Difficulty = "Medium"
    create_new: bool = False
    source_id: str | None = None
    task_type: str | None = None
    question_count: int = Field(default=20, ge=10, le=20)
    voice: VoiceVariant = "australian"


class ModuleQuestion(PteTask):
    order: int


class ModuleTest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    skill: Skill
    level: Difficulty
    questions: list[ModuleQuestion]
    total_time_seconds: int
    topic: str
    topic_source: Literal["grounded", "saved_source", "curated"]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    task_type: str | None = None
    voice: VoiceVariant = "australian"
    status: Literal["ready", "completed"] = "ready"


class ModuleAnswer(BaseModel):
    question_id: str
    answer: str = ""


class ModuleTestSubmit(BaseModel):
    answers: list[ModuleAnswer]


class Mistake(BaseModel):
    question_id: str
    task_title: str
    task_type: str
    learner_answer: str
    correct_answer: str
    explanation: str


class ModuleTestResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    test_id: str
    title: str
    skill: Skill
    correct_count: int
    wrong_count: int
    unanswered_count: int
    total_count: int
    estimated_score: int
    mistakes: list[Mistake]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TestSource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    kind: SourceKind
    mime_type: str
    topic: str
    text_preview: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TestImportQuestion(BaseModel):
    title: str
    prompt: str
    instructions: str
    response_type: ResponseType = "text"
    options: list[str] = Field(default_factory=list)
    answer_key: str = ""
    listening_script: str | None = None


class TestImportCreate(BaseModel):
    title: str
    test_kind: Literal["task", "mock"]
    skill: Skill | None = None
    task_type: str | None = None
    level: Difficulty = "Medium"
    voice: VoiceVariant = "australian"
    questions: list[TestImportQuestion] = Field(min_length=10, max_length=20)


class DeleteTests(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=50)