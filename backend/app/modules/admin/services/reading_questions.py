from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_admin_action
from app.db.models import (
    ReadingQuestion,
    ReadingQuestionAnswer,
    ReadingQuestionBlock,
    ReadingQuestionOption,
    User,
)
from app.modules.admin import repository
from app.modules.admin.schemas import QuestionAnswerIn, QuestionOptionIn, ReadingQuestionIn


async def create_reading_question(
    db: AsyncSession,
    admin_user: User,
    *,
    block_id: int,
    payload: ReadingQuestionIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, ReadingQuestionBlock, block_id, "reading_block_not_found", "Block not found")
    row = ReadingQuestion(question_block_id=block_id, **payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "reading_question", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_reading_question(
    db: AsyncSession,
    admin_user: User,
    *,
    question_id: int,
    payload: ReadingQuestionIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ReadingQuestion, question_id, "reading_question_not_found", "Question not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    await log_admin_action(db, admin_user, "update", "reading_question", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_reading_question(db: AsyncSession, admin_user: User, *, question_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ReadingQuestion, question_id, "reading_question_not_found", "Question not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "reading_question", question_id)
    await db.commit()
    return {"message": "deleted"}


async def create_reading_option(
    db: AsyncSession,
    admin_user: User,
    *,
    question_id: int,
    payload: QuestionOptionIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, ReadingQuestion, question_id, "reading_question_not_found", "Question not found")
    row = ReadingQuestionOption(question_id=question_id, **payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "reading_option", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_reading_option(
    db: AsyncSession,
    admin_user: User,
    *,
    option_id: int,
    payload: QuestionOptionIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ReadingQuestionOption, option_id, "reading_option_not_found", "Option not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    await log_admin_action(db, admin_user, "update", "reading_option", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_reading_option(db: AsyncSession, admin_user: User, *, option_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ReadingQuestionOption, option_id, "reading_option_not_found", "Option not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "reading_option", option_id)
    await db.commit()
    return {"message": "deleted"}


async def create_reading_answer(
    db: AsyncSession,
    admin_user: User,
    *,
    question_id: int,
    payload: QuestionAnswerIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, ReadingQuestion, question_id, "reading_question_not_found", "Question not found")
    row = ReadingQuestionAnswer(question_id=question_id, **payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "reading_answer", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_reading_answer(
    db: AsyncSession,
    admin_user: User,
    *,
    answer_id: int,
    payload: QuestionAnswerIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ReadingQuestionAnswer, answer_id, "reading_answer_not_found", "Answer not found")
    row.correct_answers = payload.correct_answers
    await log_admin_action(db, admin_user, "update", "reading_answer", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_reading_answer(db: AsyncSession, admin_user: User, *, answer_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ReadingQuestionAnswer, answer_id, "reading_answer_not_found", "Answer not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "reading_answer", answer_id)
    await db.commit()
    return {"message": "deleted"}
