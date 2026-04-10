from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.modules.admin.schemas import ReadingBlockIn, ReadingPassageIn
from app.modules.admin.services import reading as reading_services

from .deps import admin_dependency

router = APIRouter()


@router.post("/reading/tests/{test_id}/passages")
async def admin_create_reading_passage(
    test_id: int,
    payload: ReadingPassageIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.create_reading_passage(db, admin_user, test_id=test_id, payload=payload)


@router.patch("/reading/passages/{passage_id}")
async def admin_patch_reading_passage(
    passage_id: int,
    payload: ReadingPassageIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.patch_reading_passage(db, admin_user, passage_id=passage_id, payload=payload)


@router.delete("/reading/passages/{passage_id}")
async def admin_delete_reading_passage(
    passage_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await reading_services.delete_reading_passage(db, admin_user, passage_id=passage_id)


@router.post("/reading/passages/{passage_id}/blocks")
async def admin_create_reading_block(
    passage_id: int,
    payload: ReadingBlockIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.create_reading_block(db, admin_user, passage_id=passage_id, payload=payload)


@router.patch("/reading/blocks/{block_id}")
async def admin_patch_reading_block(
    block_id: int,
    payload: ReadingBlockIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.patch_reading_block(db, admin_user, block_id=block_id, payload=payload)


@router.delete("/reading/blocks/{block_id}")
async def admin_delete_reading_block(
    block_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await reading_services.delete_reading_block(db, admin_user, block_id=block_id)
