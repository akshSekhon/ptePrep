from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


Skill = Literal["Speaking", "Writing", "Reading", "Listening"]


class PteTask(BaseModel):
    id: str
    title: str
    skill: Skill
    task_type: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    duration_seconds: int
    prompt: str
    instructions: str
    tags: list[str] = Field(default_factory=list)


class TraitScore(BaseModel):
    label: str
    score: int
    color: str


class AttemptCreate(BaseModel):
    task_id: str
    answer_text: str = Field(min_length=1, max_length=12000)


class Attempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    task_title: str
    skill: Skill
    score: int
    traits: list[TraitScore]
    feedback: list[str]
    answer_preview: str
    word_count: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_demo: bool = True


class DashboardSummary(BaseModel):
    overall_score: int
    target_score: int
    streak_days: int
    completed_tasks: int
    today_tasks: int
    skill_scores: dict[str, int]
    weak_area: str
    recent_attempts: list[Attempt]