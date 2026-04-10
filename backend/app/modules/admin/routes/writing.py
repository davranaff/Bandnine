from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage
from app.db.models import User
from app.db.session import get_db
from app.modules.admin.schemas import WritingPartIn, WritingTestIn
from app.modules.admin.services import writing as writing_services

from .deps import admin_dependency

router = APIRouter()


@router.get("/writing/tests", response_model=CursorPage)
async def admin_list_writing_tests(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = admin_dependency(),
) -> CursorPage:
    return await writing_services.list_writing_tests(db, cursor=cursor, limit=limit)


@router.post("/writing/tests")
async def admin_create_writing_test(
    payload: WritingTestIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await writing_services.create_writing_test(db, admin_user, payload)


@router.patch("/writing/tests/{test_id}")
async def admin_patch_writing_test(
    test_id: int,
    payload: WritingTestIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await writing_services.patch_writing_test(db, admin_user, test_id=test_id, payload=payload)


@router.delete("/writing/tests/{test_id}")
async def admin_delete_writing_test(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await writing_services.delete_writing_test(db, admin_user, test_id=test_id)


@router.post("/writing/tests/{test_id}/parts")
async def admin_create_writing_part(
    test_id: int,
    payload: WritingPartIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await writing_services.create_writing_part(db, admin_user, test_id=test_id, payload=payload)


@router.patch("/writing/parts/{part_id}")
async def admin_patch_writing_part(
    part_id: int,
    payload: WritingPartIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await writing_services.patch_writing_part(db, admin_user, part_id=part_id, payload=payload)


@router.delete("/writing/parts/{part_id}")
async def admin_delete_writing_part(
    part_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await writing_services.delete_writing_part(db, admin_user, part_id=part_id)
