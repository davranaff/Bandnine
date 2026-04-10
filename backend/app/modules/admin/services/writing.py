from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_admin_action
from app.core.pagination import CursorPage, paginate_query, serialize_page
from app.db.models import User, WritingPart, WritingTest
from app.modules.admin import repository
from app.modules.admin.schemas import WritingPartIn, WritingTestIn


async def list_writing_tests(
    db: AsyncSession,
    *,
    cursor: str | None,
    limit: int,
) -> CursorPage:
    rows, next_cursor = await paginate_query(db, select(WritingTest), WritingTest.id, limit, cursor)
    return serialize_page(
        rows,
        serializer=lambda row: {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "time_limit": row.time_limit,
            "is_active": row.is_active,
        },
        next_cursor=next_cursor,
        limit=limit,
    )


async def create_writing_test(db: AsyncSession, admin_user: User, payload: WritingTestIn) -> dict[str, Any]:
    row = WritingTest(**payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "writing_test", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_writing_test(
    db: AsyncSession,
    admin_user: User,
    *,
    test_id: int,
    payload: WritingTestIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, WritingTest, test_id, "writing_test_not_found", "Writing test not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    await log_admin_action(db, admin_user, "update", "writing_test", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_writing_test(db: AsyncSession, admin_user: User, *, test_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, WritingTest, test_id, "writing_test_not_found", "Writing test not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "writing_test", test_id)
    await db.commit()
    return {"message": "deleted"}


async def create_writing_part(
    db: AsyncSession,
    admin_user: User,
    *,
    test_id: int,
    payload: WritingPartIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, WritingTest, test_id, "writing_test_not_found", "Writing test not found")
    row = WritingPart(test_id=test_id, **payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "writing_part", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_writing_part(
    db: AsyncSession,
    admin_user: User,
    *,
    part_id: int,
    payload: WritingPartIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, WritingPart, part_id, "writing_part_not_found", "Part not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    await log_admin_action(db, admin_user, "update", "writing_part", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_writing_part(db: AsyncSession, admin_user: User, *, part_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, WritingPart, part_id, "writing_part_not_found", "Part not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "writing_part", part_id)
    await db.commit()
    return {"message": "deleted"}
