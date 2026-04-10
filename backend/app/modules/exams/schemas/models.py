from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

ExamKind = Literal["reading", "listening", "writing"]


class ExamCreateIn(BaseModel):
    test_id: int = Field(gt=0)


class ExamAnswerIn(BaseModel):
    id: int = Field(gt=0)
    value: str


class WritingPartSubmitIn(BaseModel):
    part_id: int = Field(gt=0)
    essay: str


class ExamSubmitOut(BaseModel):
    answers: list[dict[str, Any]]
    score: float | None
    correct_answers: int | None
    time_spent: float | None


class ExamPublic(BaseModel):
    id: int
    user_id: int
    started_at: datetime | None
    finished_at: datetime | None
    finish_reason: str | None
    test_id: int
    kind: ExamKind


class ExamsMeOut(BaseModel):
    reading: dict[str, Any]
    listening: dict[str, Any]
    writing: dict[str, Any]
