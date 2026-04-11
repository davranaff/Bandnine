from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage, serialize_page
from app.db.models import User, UserAnalytics, UserProfile, UserProgress
from app.modules.profile import repository
from app.modules.profile.schemas import AnalyticsOut, ProfileOut, ProgressOut


def _profile_out(profile: UserProfile) -> ProfileOut:
    return ProfileOut(
        id=profile.id,
        user_id=profile.user_id,
        date_of_birth=profile.date_of_birth,
        country=profile.country,
        native_language=profile.native_language,
        target_band_score=profile.target_band_score,
    )


def _progress_out(row: UserProgress) -> ProgressOut:
    return ProgressOut(
        id=row.id,
        test_date=row.test_date,
        band_score=row.band_score,
        correct_answers=row.correct_answers,
        total_questions=row.total_questions,
        time_taken_seconds=row.time_taken_seconds,
        test_type=row.test_type,
    )


def _analytics_out(row: UserAnalytics) -> AnalyticsOut:
    return AnalyticsOut(
        total_tests_taken=row.total_tests_taken,
        average_band_score=row.average_band_score,
        best_band_score=row.best_band_score,
        total_study_time_seconds=row.total_study_time_seconds,
        last_test_date=row.last_test_date,
    )


async def get_or_create_profile(db: AsyncSession, user: User) -> UserProfile:
    profile = await repository.get_profile_by_user_id(db, user.id)
    if profile is None:
        profile = await repository.create_profile(db, user.id)
    return profile


async def get_or_create_analytics(db: AsyncSession, user: User) -> UserAnalytics:
    analytics = await repository.get_analytics_by_user_id(db, user.id)
    if analytics is None:
        analytics = await repository.create_analytics(db, user.id)
    return analytics


async def patch_profile(db: AsyncSession, user: User, payload: dict) -> ProfileOut:
    profile = await get_or_create_profile(db, user)
    for key, value in payload.items():
        setattr(profile, key, value)
    await db.commit()
    await db.refresh(profile)
    return _profile_out(profile)


async def list_progress(db: AsyncSession, user: User, offset: int, limit: int) -> CursorPage:
    rows = await repository.list_progress_by_user_id(
        db,
        user_id=user.id,
        offset=offset,
        limit=limit,
    )
    return serialize_page(
        rows,
        serializer=lambda row: _progress_out(row).model_dump(),
        limit=limit,
        offset=offset,
    )


async def create_progress(db: AsyncSession, user: User, payload: dict) -> ProgressOut:
    progress = UserProgress(
        user_id=user.id,
        test_date=datetime.now(UTC),
        band_score=payload["band_score"],
        correct_answers=payload.get("correct_answers"),
        total_questions=payload.get("total_questions"),
        time_taken_seconds=payload.get("time_taken_seconds"),
        test_type=payload["test_type"],
    )
    db.add(progress)
    await db.flush()

    analytics = await get_or_create_analytics(db, user)
    analytics.total_tests_taken += 1
    analytics.best_band_score = max(analytics.best_band_score, progress.band_score)
    analytics.total_study_time_seconds += progress.time_taken_seconds or 0
    analytics.last_test_date = progress.test_date

    total = analytics.average_band_score * Decimal(analytics.total_tests_taken - 1)
    analytics.average_band_score = (total + progress.band_score) / Decimal(analytics.total_tests_taken)

    await db.commit()
    await db.refresh(progress)
    return _progress_out(progress)


async def get_analytics(db: AsyncSession, user: User) -> AnalyticsOut:
    analytics = await get_or_create_analytics(db, user)
    return _analytics_out(analytics)


async def get_dashboard(db: AsyncSession, user: User) -> dict:
    profile = await get_or_create_profile(db, user)
    analytics = await get_or_create_analytics(db, user)

    recent_progress = await repository.list_recent_progress(db, user_id=user.id, limit=5)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        },
        "profile": _profile_out(profile),
        "recent_progress": [_progress_out(item) for item in recent_progress],
        "analytics": _analytics_out(analytics),
    }
