from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_admin_action
from app.db.models import ParseStatusEnum, ReadingPassage, ReadingQuestionBlock, ReadingTest, User
from app.modules.admin import repository
from app.modules.admin.schemas import ReadingBlockIn, ReadingPassageIn
from app.workers.queue import enqueue_table_parse


async def create_reading_passage(
    db: AsyncSession,
    admin_user: User,
    *,
    test_id: int,
    payload: ReadingPassageIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, ReadingTest, test_id, "reading_test_not_found", "Reading test not found")
    row = ReadingPassage(test_id=test_id, **payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "reading_passage", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_reading_passage(
    db: AsyncSession,
    admin_user: User,
    *,
    passage_id: int,
    payload: ReadingPassageIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ReadingPassage, passage_id, "reading_passage_not_found", "Passage not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    await log_admin_action(db, admin_user, "update", "reading_passage", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_reading_passage(db: AsyncSession, admin_user: User, *, passage_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ReadingPassage, passage_id, "reading_passage_not_found", "Passage not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "reading_passage", passage_id)
    await db.commit()
    return {"message": "deleted"}


async def create_reading_block(
    db: AsyncSession,
    admin_user: User,
    *,
    passage_id: int,
    payload: ReadingBlockIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, ReadingPassage, passage_id, "reading_passage_not_found", "Passage not found")
    row = ReadingQuestionBlock(passage_id=passage_id, **payload.model_dump())
    if row.table_completion:
        row.parse_status = ParseStatusEnum.pending
    db.add(row)
    await db.flush()
    if row.table_completion:
        await enqueue_table_parse("reading", row.id)
    await log_admin_action(db, admin_user, "create", "reading_block", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_reading_block(
    db: AsyncSession,
    admin_user: User,
    *,
    block_id: int,
    payload: ReadingBlockIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ReadingQuestionBlock, block_id, "reading_block_not_found", "Block not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    if payload.table_completion is not None:
        row.parse_status = ParseStatusEnum.pending
        await enqueue_table_parse("reading", row.id)
    await log_admin_action(db, admin_user, "update", "reading_block", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_reading_block(db: AsyncSession, admin_user: User, *, block_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ReadingQuestionBlock, block_id, "reading_block_not_found", "Block not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "reading_block", block_id)
    await db.commit()
    return {"message": "deleted"}
