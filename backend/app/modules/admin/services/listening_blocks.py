from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_admin_action
from app.db.models import ListeningPart, ListeningQuestionBlock, ParseStatusEnum, User
from app.modules.admin import repository
from app.modules.admin.schemas import ListeningBlockIn
from app.modules.admin.services.validation import validate_listening_block_payload
from app.workers.queue import enqueue_table_parse


async def create_listening_block(
    db: AsyncSession,
    admin_user: User,
    *,
    part_id: int,
    payload: ListeningBlockIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, ListeningPart, part_id, "listening_part_not_found", "Part not found")
    validate_listening_block_payload(payload)
    row = ListeningQuestionBlock(part_id=part_id, **payload.model_dump())
    if row.table_completion:
        row.parse_status = ParseStatusEnum.pending
    db.add(row)
    await db.flush()
    if row.table_completion:
        await enqueue_table_parse("listening", row.id)
    await log_admin_action(db, admin_user, "create", "listening_block", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_listening_block(
    db: AsyncSession,
    admin_user: User,
    *,
    block_id: int,
    payload: ListeningBlockIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ListeningQuestionBlock, block_id, "listening_block_not_found", "Block not found")
    validate_listening_block_payload(payload)
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    if payload.table_completion is not None:
        row.parse_status = ParseStatusEnum.pending
        await enqueue_table_parse("listening", row.id)
    await log_admin_action(db, admin_user, "update", "listening_block", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_listening_block(db: AsyncSession, admin_user: User, *, block_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ListeningQuestionBlock, block_id, "listening_block_not_found", "Block not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "listening_block", block_id)
    await db.commit()
    return {"message": "deleted"}
