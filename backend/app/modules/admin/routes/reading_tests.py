from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage
from app.db.models import User
from app.db.session import get_db
from app.modules.admin.schemas import ReadingTestIn
from app.modules.admin.services import reading as reading_services

from .deps import admin_dependency

router = APIRouter()


@router.get("/reading/tests", response_model=CursorPage)
async def admin_list_reading_tests(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = admin_dependency(),
) -> CursorPage:
    return await reading_services.list_reading_tests(db, cursor=cursor, limit=limit)


@router.post("/reading/tests")
async def admin_create_reading_test(
    payload: ReadingTestIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.create_reading_test(db, admin_user, payload)


@router.get("/reading/tests/{test_id}")
async def admin_get_reading_test(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.get_reading_test(db, test_id)


@router.patch("/reading/tests/{test_id}")
async def admin_patch_reading_test(
    test_id: int,
    payload: ReadingTestIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.patch_reading_test(db, admin_user, test_id=test_id, payload=payload)


@router.delete("/reading/tests/{test_id}")
async def admin_delete_reading_test(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await reading_services.delete_reading_test(db, admin_user, test_id=test_id)
