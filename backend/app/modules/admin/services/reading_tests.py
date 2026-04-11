from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_admin_action
from app.core.pagination import CursorPage, paginate_query, serialize_page
from app.db.models import ReadingTest, User
from app.modules.admin import repository
from app.modules.admin.schemas import ReadingTestIn


async def list_reading_tests(
    db: AsyncSession,
    *,
    offset: int,
    limit: int,
) -> CursorPage:
    rows = await paginate_query(db, select(ReadingTest), ReadingTest.id, limit, offset)
    return serialize_page(
        rows,
        serializer=lambda row: {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "time_limit": row.time_limit,
            "is_active": row.is_active,
        },
        limit=limit,
        offset=offset,
    )


async def create_reading_test(db: AsyncSession, admin_user: User, payload: ReadingTestIn) -> dict[str, Any]:
    item = ReadingTest(**payload.model_dump())
    db.add(item)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "reading_test", item.id, payload.model_dump())
    await db.commit()
    return {"id": item.id}


async def get_reading_test(db: AsyncSession, test_id: int) -> dict[str, Any]:
    row = await repository.get_or_404(db, ReadingTest, test_id, "reading_test_not_found", "Reading test not found")
    return {
        "id": row.id,
        "title": row.title,
        "description": row.description,
        "time_limit": row.time_limit,
        "is_active": row.is_active,
    }


async def patch_reading_test(
    db: AsyncSession,
    admin_user: User,
    *,
    test_id: int,
    payload: ReadingTestIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ReadingTest, test_id, "reading_test_not_found", "Reading test not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    await log_admin_action(db, admin_user, "update", "reading_test", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_reading_test(db: AsyncSession, admin_user: User, *, test_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ReadingTest, test_id, "reading_test_not_found", "Reading test not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "reading_test", test_id)
    await db.commit()
    return {"message": "deleted"}
