from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.modules.admin.schemas import ListeningQuestionIn, QuestionAnswerIn, QuestionOptionIn
from app.modules.admin.services import listening as listening_services

from .deps import admin_dependency

router = APIRouter()


@router.post("/listening/blocks/{block_id}/questions")
async def admin_create_listening_question(
    block_id: int,
    payload: ListeningQuestionIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.create_listening_question(db, admin_user, block_id=block_id, payload=payload)


@router.patch("/listening/questions/{question_id}")
async def admin_patch_listening_question(
    question_id: int,
    payload: ListeningQuestionIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.patch_listening_question(db, admin_user, question_id=question_id, payload=payload)


@router.delete("/listening/questions/{question_id}")
async def admin_delete_listening_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await listening_services.delete_listening_question(db, admin_user, question_id=question_id)


@router.post("/listening/questions/{question_id}/options")
async def admin_create_listening_option(
    question_id: int,
    payload: QuestionOptionIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.create_listening_option(db, admin_user, question_id=question_id, payload=payload)


@router.patch("/listening/options/{option_id}")
async def admin_patch_listening_option(
    option_id: int,
    payload: QuestionOptionIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.patch_listening_option(db, admin_user, option_id=option_id, payload=payload)


@router.delete("/listening/options/{option_id}")
async def admin_delete_listening_option(
    option_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await listening_services.delete_listening_option(db, admin_user, option_id=option_id)


@router.post("/listening/questions/{question_id}/answers")
async def admin_create_listening_answer(
    question_id: int,
    payload: QuestionAnswerIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.create_listening_answer(db, admin_user, question_id=question_id, payload=payload)


@router.patch("/listening/answers/{answer_id}")
async def admin_patch_listening_answer(
    answer_id: int,
    payload: QuestionAnswerIn,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, Any]:
    return await listening_services.patch_listening_answer(db, admin_user, answer_id=answer_id, payload=payload)


@router.delete("/listening/answers/{answer_id}")
async def admin_delete_listening_answer(
    answer_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = admin_dependency(),
) -> dict[str, str]:
    return await listening_services.delete_listening_answer(db, admin_user, answer_id=answer_id)
