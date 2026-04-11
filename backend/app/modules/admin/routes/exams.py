from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage
from app.db.models import User
from app.db.session import get_db
from app.modules.admin.schemas import WritingReviewIn
from app.modules.admin.services import exams as exam_services

from .deps import admin_dependency

router = APIRouter()


@router.get("/exams/{kind}", response_model=CursorPage)
async def admin_list_exams(
    kind: Literal["reading", "listening", "writing"],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = admin_dependency(),
) -> CursorPage:
    return await exam_services.list_exams(db, kind=kind, offset=offset, limit=limit)


@router.get("/exams/{kind}/{exam_id}")
async def admin_get_exam(
    kind: Literal["reading", "listening", "writing"],
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = admin_dependency(),
) -> dict[str, Any]:
    return await exam_services.get_exam(db, kind=kind, exam_id=exam_id)


@router.patch("/exams/writing/parts/{exam_part_id}/review")
async def admin_review_writing_part(
    exam_part_id: int,
    payload: WritingReviewIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await exam_services.review_writing_part(db, admin_user, exam_part_id=exam_part_id, payload=payload)
