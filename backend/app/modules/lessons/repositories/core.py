from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import paginate_query
from app.db.models import Category, Lesson


async def list_categories(
    db: AsyncSession,
    *,
    offset: int,
    limit: int,
) -> list[Category]:
    return await paginate_query(db, select(Category), Category.id, limit, offset)


async def get_category_by_slug(db: AsyncSession, slug: str) -> Category | None:
    return (await db.execute(select(Category).where(Category.slug == slug))).scalar_one_or_none()


async def list_lessons_by_category(
    db: AsyncSession,
    *,
    category_id: int,
    offset: int,
    limit: int,
) -> list[Lesson]:
    return await paginate_query(
        db,
        select(Lesson).where(Lesson.category_id == category_id),
        Lesson.id,
        limit,
        offset,
    )

