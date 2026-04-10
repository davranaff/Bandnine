from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.modules.admin.schemas import ListeningBlockIn
from app.modules.admin.services import listening as listening_services

from .deps import admin_dependency

router = APIRouter()


@router.post("/listening/parts/{part_id}/blocks")
async def admin_create_listening_block(
    part_id: int,
    payload: ListeningBlockIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.create_listening_block(db, admin_user, part_id=part_id, payload=payload)


@router.patch("/listening/blocks/{block_id}")
async def admin_patch_listening_block(
    block_id: int,
    payload: ListeningBlockIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.patch_listening_block(db, admin_user, block_id=block_id, payload=payload)


@router.delete("/listening/blocks/{block_id}")
async def admin_delete_listening_block(
    block_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await listening_services.delete_listening_block(db, admin_user, block_id=block_id)
