from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import paginate_query
from app.db.models import ReadingPassage, ReadingQuestion, ReadingQuestionBlock, ReadingTest


async def list_active_tests(
    db: AsyncSession,
    *,
    offset: int,
    limit: int,
) -> list[ReadingTest]:
    stmt = select(ReadingTest).where(ReadingTest.is_active.is_(True))
    return await paginate_query(db, stmt, ReadingTest.id, limit, offset)


async def get_test_detail(db: AsyncSession, test_id: int) -> ReadingTest | None:
    stmt = (
        select(ReadingTest)
        .where(ReadingTest.id == test_id)
        .options(
            selectinload(ReadingTest.passages)
            .selectinload(ReadingPassage.question_blocks)
            .selectinload(ReadingQuestionBlock.questions)
            .selectinload(ReadingQuestion.options),
            selectinload(ReadingTest.passages)
            .selectinload(ReadingPassage.question_blocks)
            .selectinload(ReadingQuestionBlock.questions)
            .selectinload(ReadingQuestion.answers),
        )
    )
    return (await db.execute(stmt)).scalar_one_or_none()

