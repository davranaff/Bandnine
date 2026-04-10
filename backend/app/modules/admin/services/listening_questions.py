from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_admin_action
from app.db.models import (
    ListeningQuestion,
    ListeningQuestionAnswer,
    ListeningQuestionBlock,
    ListeningQuestionOption,
    User,
)
from app.modules.admin import repository
from app.modules.admin.schemas import ListeningQuestionIn, QuestionAnswerIn, QuestionOptionIn


async def create_listening_question(
    db: AsyncSession,
    admin_user: User,
    *,
    block_id: int,
    payload: ListeningQuestionIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, ListeningQuestionBlock, block_id, "listening_block_not_found", "Block not found")
    row = ListeningQuestion(question_block_id=block_id, **payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "listening_question", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_listening_question(
    db: AsyncSession,
    admin_user: User,
    *,
    question_id: int,
    payload: ListeningQuestionIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ListeningQuestion, question_id, "listening_question_not_found", "Question not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    await log_admin_action(db, admin_user, "update", "listening_question", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_listening_question(db: AsyncSession, admin_user: User, *, question_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ListeningQuestion, question_id, "listening_question_not_found", "Question not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "listening_question", question_id)
    await db.commit()
    return {"message": "deleted"}


async def create_listening_option(
    db: AsyncSession,
    admin_user: User,
    *,
    question_id: int,
    payload: QuestionOptionIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, ListeningQuestion, question_id, "listening_question_not_found", "Question not found")
    row = ListeningQuestionOption(question_id=question_id, **payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "listening_option", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_listening_option(
    db: AsyncSession,
    admin_user: User,
    *,
    option_id: int,
    payload: QuestionOptionIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ListeningQuestionOption, option_id, "listening_option_not_found", "Option not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    await log_admin_action(db, admin_user, "update", "listening_option", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_listening_option(db: AsyncSession, admin_user: User, *, option_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ListeningQuestionOption, option_id, "listening_option_not_found", "Option not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "listening_option", option_id)
    await db.commit()
    return {"message": "deleted"}


async def create_listening_answer(
    db: AsyncSession,
    admin_user: User,
    *,
    question_id: int,
    payload: QuestionAnswerIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, ListeningQuestion, question_id, "listening_question_not_found", "Question not found")
    row = ListeningQuestionAnswer(question_id=question_id, **payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "listening_answer", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_listening_answer(
    db: AsyncSession,
    admin_user: User,
    *,
    answer_id: int,
    payload: QuestionAnswerIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ListeningQuestionAnswer, answer_id, "listening_answer_not_found", "Answer not found")
    row.correct_answers = payload.correct_answers
    await log_admin_action(db, admin_user, "update", "listening_answer", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_listening_answer(db: AsyncSession, admin_user: User, *, answer_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ListeningQuestionAnswer, answer_id, "listening_answer_not_found", "Answer not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "listening_answer", answer_id)
    await db.commit()
    return {"message": "deleted"}
