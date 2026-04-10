from __future__ import annotations

from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_admin_action
from app.core.pagination import CursorPage, paginate_query, serialize_page
from app.db.models import ListeningExam, ReadingExam, User, WritingExam, WritingExamPart
from app.modules.admin import repository
from app.modules.admin.schemas import WritingReviewIn
from app.modules.exams.services import _serialize_exam_summary


def _resolve_exam_model(kind: Literal["reading", "listening", "writing"]):
    if kind == "reading":
        return ReadingExam
    if kind == "listening":
        return ListeningExam
    return WritingExam


async def list_exams(
    db: AsyncSession,
    *,
    kind: Literal["reading", "listening", "writing"],
    cursor: str | None,
    limit: int,
) -> CursorPage:
    model = _resolve_exam_model(kind)
    rows, next_cursor = await paginate_query(db, select(model), model.id, limit, cursor)
    return serialize_page(
        rows,
        serializer=lambda row: _serialize_exam_summary(kind, row),
        next_cursor=next_cursor,
        limit=limit,
    )


async def get_exam(
    db: AsyncSession,
    *,
    kind: Literal["reading", "listening", "writing"],
    exam_id: int,
) -> dict[str, Any]:
    model = _resolve_exam_model(kind)
    row = await repository.get_or_404(db, model, exam_id, "exam_not_found", "Exam not found")
    return _serialize_exam_summary(kind, row)


async def review_writing_part(
    db: AsyncSession,
    admin_user: User,
    *,
    exam_part_id: int,
    payload: WritingReviewIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(
        db,
        WritingExamPart,
        exam_part_id,
        "writing_exam_part_not_found",
        "Exam part not found",
    )
    row.is_checked = payload.is_checked
    row.corrections = payload.corrections
    row.score = payload.score
    await log_admin_action(db, admin_user, "review", "writing_exam_part", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}
