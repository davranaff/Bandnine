from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import paginate_query
from app.db.models import UserAnalytics, UserProfile, UserProgress


async def get_profile_by_user_id(db: AsyncSession, user_id: int) -> UserProfile | None:
    return (await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))).scalar_one_or_none()


async def create_profile(db: AsyncSession, user_id: int) -> UserProfile:
    profile = UserProfile(user_id=user_id)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_analytics_by_user_id(db: AsyncSession, user_id: int) -> UserAnalytics | None:
    return (await db.execute(select(UserAnalytics).where(UserAnalytics.user_id == user_id))).scalar_one_or_none()


async def create_analytics(db: AsyncSession, user_id: int) -> UserAnalytics:
    analytics = UserAnalytics(user_id=user_id)
    db.add(analytics)
    await db.commit()
    await db.refresh(analytics)
    return analytics


async def list_progress_by_user_id(
    db: AsyncSession,
    *,
    user_id: int,
    offset: int,
    limit: int,
) -> list[UserProgress]:
    stmt = select(UserProgress).where(UserProgress.user_id == user_id)
    return await paginate_query(db, stmt, UserProgress.id, limit, offset)


async def list_recent_progress(db: AsyncSession, *, user_id: int, limit: int) -> list[UserProgress]:
    rows = (
        await db.execute(
            select(UserProgress)
            .where(UserProgress.user_id == user_id)
            .order_by(UserProgress.test_date.desc())
            .limit(limit)
        )
    ).scalars()
    return list(rows)

