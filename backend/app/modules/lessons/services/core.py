from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ApiError
from app.core.pagination import CursorPage, serialize_page
from app.modules.lessons import repository
from app.modules.lessons.schemas import CategoryOut, LessonOut


async def list_categories(
    db: AsyncSession,
    *,
    offset: int,
    limit: int,
) -> CursorPage:
    rows = await repository.list_categories(db, offset=offset, limit=limit)
    return serialize_page(
        rows,
        serializer=lambda row: CategoryOut(id=row.id, title=row.title, slug=row.slug).model_dump(),
        limit=limit,
        offset=offset,
    )


async def list_lessons_by_category(
    db: AsyncSession,
    *,
    slug: str,
    offset: int,
    limit: int,
) -> CursorPage:
    category = await repository.get_category_by_slug(db, slug)
    if category is None:
        raise ApiError(code="category_not_found", message="Category not found", status_code=404)

    rows = await repository.list_lessons_by_category(
        db,
        category_id=category.id,
        offset=offset,
        limit=limit,
    )
    return serialize_page(
        rows,
        serializer=lambda row: LessonOut(
            id=row.id,
            category_id=row.category_id,
            title=row.title,
            video_link=row.video_link,
        ).model_dump(),
        limit=limit,
        offset=offset,
    )

