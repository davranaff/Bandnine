from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage
from app.db.models import User
from app.db.session import get_db
from app.modules.admin.schemas import ListeningPartIn, ListeningTestIn
from app.modules.admin.services import listening as listening_services

from .deps import admin_dependency

router = APIRouter()


@router.get("/listening/tests", response_model=CursorPage)
async def admin_list_listening_tests(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = admin_dependency(),
) -> CursorPage:
    return await listening_services.list_listening_tests(db, cursor=cursor, limit=limit)


@router.post("/listening/tests")
async def admin_create_listening_test(
    payload: ListeningTestIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.create_listening_test(db, admin_user, payload)


@router.patch("/listening/tests/{test_id}")
async def admin_patch_listening_test(
    test_id: int,
    payload: ListeningTestIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.patch_listening_test(db, admin_user, test_id=test_id, payload=payload)


@router.delete("/listening/tests/{test_id}")
async def admin_delete_listening_test(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await listening_services.delete_listening_test(db, admin_user, test_id=test_id)


@router.post("/listening/tests/{test_id}/parts")
async def admin_create_listening_part(
    test_id: int,
    payload: ListeningPartIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.create_listening_part(db, admin_user, test_id=test_id, payload=payload)


@router.patch("/listening/parts/{part_id}")
async def admin_patch_listening_part(
    part_id: int,
    payload: ListeningPartIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.patch_listening_part(db, admin_user, part_id=part_id, payload=payload)


@router.delete("/listening/parts/{part_id}")
async def admin_delete_listening_part(
    part_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await listening_services.delete_listening_part(db, admin_user, part_id=part_id)
