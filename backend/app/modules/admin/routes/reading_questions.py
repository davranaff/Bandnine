from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.modules.admin.schemas import QuestionAnswerIn, QuestionOptionIn, ReadingQuestionIn
from app.modules.admin.services import reading as reading_services

from .deps import admin_dependency

router = APIRouter()


@router.post("/reading/blocks/{block_id}/questions")
async def admin_create_reading_question(
    block_id: int,
    payload: ReadingQuestionIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.create_reading_question(db, admin_user, block_id=block_id, payload=payload)


@router.patch("/reading/questions/{question_id}")
async def admin_patch_reading_question(
    question_id: int,
    payload: ReadingQuestionIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.patch_reading_question(db, admin_user, question_id=question_id, payload=payload)


@router.delete("/reading/questions/{question_id}")
async def admin_delete_reading_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await reading_services.delete_reading_question(db, admin_user, question_id=question_id)


@router.post("/reading/questions/{question_id}/options")
async def admin_create_reading_option(
    question_id: int,
    payload: QuestionOptionIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.create_reading_option(db, admin_user, question_id=question_id, payload=payload)


@router.patch("/reading/options/{option_id}")
async def admin_patch_reading_option(
    option_id: int,
    payload: QuestionOptionIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.patch_reading_option(db, admin_user, option_id=option_id, payload=payload)


@router.delete("/reading/options/{option_id}")
async def admin_delete_reading_option(
    option_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await reading_services.delete_reading_option(db, admin_user, option_id=option_id)


@router.post("/reading/questions/{question_id}/answers")
async def admin_create_reading_answer(
    question_id: int,
    payload: QuestionAnswerIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.create_reading_answer(db, admin_user, question_id=question_id, payload=payload)


@router.patch("/reading/answers/{answer_id}")
async def admin_patch_reading_answer(
    answer_id: int,
    payload: QuestionAnswerIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await reading_services.patch_reading_answer(db, admin_user, answer_id=answer_id, payload=payload)


@router.delete("/reading/answers/{answer_id}")
async def admin_delete_reading_answer(
    answer_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await reading_services.delete_reading_answer(db, admin_user, answer_id=answer_id)
