from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import paginate_query
from app.db.models import ListeningPart, ListeningQuestion, ListeningQuestionBlock, ListeningTest


async def list_active_tests(
    db: AsyncSession,
    *,
    cursor: str | None,
    limit: int,
) -> tuple[list[ListeningTest], str | None]:
    stmt = select(ListeningTest).where(ListeningTest.is_active.is_(True))
    return await paginate_query(db, stmt, ListeningTest.id, limit, cursor)


async def get_test_detail(db: AsyncSession, test_id: int) -> ListeningTest | None:
    stmt = (
        select(ListeningTest)
        .where(ListeningTest.id == test_id)
        .options(
            selectinload(ListeningTest.parts)
            .selectinload(ListeningPart.question_blocks)
            .selectinload(ListeningQuestionBlock.questions)
            .selectinload(ListeningQuestion.options),
            selectinload(ListeningTest.parts)
            .selectinload(ListeningPart.question_blocks)
            .selectinload(ListeningQuestionBlock.questions)
            .selectinload(ListeningQuestion.answers),
        )
    )
    return (await db.execute(stmt)).scalar_one_or_none()

