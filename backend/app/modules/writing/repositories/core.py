from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import paginate_query
from app.db.models import WritingTest


async def list_active_tests(
    db: AsyncSession,
    *,
    cursor: str | None,
    limit: int,
) -> tuple[list[WritingTest], str | None]:
    stmt = select(WritingTest).where(WritingTest.is_active.is_(True))
    return await paginate_query(db, stmt, WritingTest.id, limit, cursor)


async def get_test_detail(db: AsyncSession, test_id: int) -> WritingTest | None:
    stmt = select(WritingTest).where(WritingTest.id == test_id).options(selectinload(WritingTest.writing_parts))
    return (await db.execute(stmt)).scalar_one_or_none()

