from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_admin_action
from app.core.pagination import CursorPage, paginate_query, serialize_page
from app.db.models import Category, Lesson, User
from app.modules.admin import repository
from app.modules.admin.schemas import CategoryIn, LessonIn


async def list_categories(
    db: AsyncSession,
    *,
    cursor: str | None,
    limit: int,
) -> CursorPage:
    rows, next_cursor = await paginate_query(db, select(Category), Category.id, limit, cursor)
    return serialize_page(
        rows,
        serializer=lambda row: {"id": row.id, "title": row.title, "slug": row.slug},
        next_cursor=next_cursor,
        limit=limit,
    )


async def create_category(db: AsyncSession, admin_user: User, payload: CategoryIn) -> dict[str, Any]:
    row = Category(**payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "category", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_category(
    db: AsyncSession,
    admin_user: User,
    *,
    category_id: int,
    payload: CategoryIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, Category, category_id, "category_not_found", "Category not found")
    row.title = payload.title
    row.slug = payload.slug
    await log_admin_action(db, admin_user, "update", "category", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_category(db: AsyncSession, admin_user: User, *, category_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, Category, category_id, "category_not_found", "Category not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "category", category_id)
    await db.commit()
    return {"message": "deleted"}


async def list_lessons(
    db: AsyncSession,
    *,
    cursor: str | None,
    limit: int,
) -> CursorPage:
    rows, next_cursor = await paginate_query(db, select(Lesson), Lesson.id, limit, cursor)
    return serialize_page(
        rows,
        serializer=lambda row: {
            "id": row.id,
            "category_id": row.category_id,
            "title": row.title,
            "video_link": row.video_link,
        },
        next_cursor=next_cursor,
        limit=limit,
    )


async def create_lesson(db: AsyncSession, admin_user: User, payload: LessonIn) -> dict[str, Any]:
    await repository.get_or_404(db, Category, payload.category_id, "category_not_found", "Category not found")
    row = Lesson(**payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "lesson", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_lesson(
    db: AsyncSession,
    admin_user: User,
    *,
    lesson_id: int,
    payload: LessonIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, Lesson, lesson_id, "lesson_not_found", "Lesson not found")
    await repository.get_or_404(db, Category, payload.category_id, "category_not_found", "Category not found")
    row.category_id = payload.category_id
    row.title = payload.title
    row.video_link = payload.video_link
    await log_admin_action(db, admin_user, "update", "lesson", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_lesson(db: AsyncSession, admin_user: User, *, lesson_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, Lesson, lesson_id, "lesson_not_found", "Lesson not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "lesson", lesson_id)
    await db.commit()
    return {"message": "deleted"}
