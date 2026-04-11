from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage
from app.db.models import User
from app.db.session import get_db
from app.modules.admin.schemas import CategoryIn, LessonIn
from app.modules.admin.services import lessons as lessons_services

from .deps import admin_dependency

router = APIRouter()


@router.get("/lessons/categories", response_model=CursorPage)
async def admin_list_categories(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = admin_dependency(),
) -> CursorPage:
    return await lessons_services.list_categories(db, offset=offset, limit=limit)


@router.post("/lessons/categories")
async def admin_create_category(
    payload: CategoryIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await lessons_services.create_category(db, admin_user, payload)


@router.patch("/lessons/categories/{category_id}")
async def admin_patch_category(
    category_id: int,
    payload: CategoryIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await lessons_services.patch_category(db, admin_user, category_id=category_id, payload=payload)


@router.delete("/lessons/categories/{category_id}")
async def admin_delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await lessons_services.delete_category(db, admin_user, category_id=category_id)


@router.get("/lessons", response_model=CursorPage)
async def admin_list_lessons(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = admin_dependency(),
) -> CursorPage:
    return await lessons_services.list_lessons(db, offset=offset, limit=limit)


@router.post("/lessons")
async def admin_create_lesson(
    payload: LessonIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await lessons_services.create_lesson(db, admin_user, payload)


@router.patch("/lessons/{lesson_id}")
async def admin_patch_lesson(
    lesson_id: int,
    payload: LessonIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await lessons_services.patch_lesson(db, admin_user, lesson_id=lesson_id, payload=payload)


@router.delete("/lessons/{lesson_id}")
async def admin_delete_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await lessons_services.delete_lesson(db, admin_user, lesson_id=lesson_id)
