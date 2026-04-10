from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.db.models import ProgressTestTypeEnum


class ProfileOut(BaseModel):
    id: int
    user_id: int
    date_of_birth: date | None
    country: str
    native_language: str
    target_band_score: Decimal


class ProfilePatchIn(BaseModel):
    date_of_birth: date | None = None
    country: str | None = None
    native_language: str | None = None
    target_band_score: Decimal | None = None


class ProgressIn(BaseModel):
    band_score: Decimal
    correct_answers: int | None = None
    total_questions: int | None = None
    time_taken_seconds: int | None = None
    test_type: ProgressTestTypeEnum


class ProgressOut(BaseModel):
    id: int
    test_date: datetime
    band_score: Decimal
    correct_answers: int | None
    total_questions: int | None
    time_taken_seconds: int | None
    test_type: ProgressTestTypeEnum


class AnalyticsOut(BaseModel):
    total_tests_taken: int
    average_band_score: Decimal
    best_band_score: Decimal
    total_study_time_seconds: int
    last_test_date: datetime | None


class DashboardOut(BaseModel):
    user: dict
    profile: ProfileOut
    recent_progress: list[ProgressOut]
    analytics: AnalyticsOut
