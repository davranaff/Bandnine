from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
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
from app.modules.admin.services.validation import (
    ensure_answers_supported,
    ensure_options_supported,
    ensure_single_correct_option_limit,
    validate_correct_answer_text,
    validate_option_text,
)


async def _resolve_question_block_type(db: AsyncSession, question_id: int) -> str:
    question = await repository.get_or_404(db, ReadingQuestion, question_id, "reading_question_not_found", "Question not found")
    block = await repository.get_or_404(
        db,
        ReadingQuestionBlock,
        question.question_block_id,
        "reading_block_not_found",
        "Block not found",
    )
    return block.block_type


async def _count_correct_options(db: AsyncSession, *, question_id: int, exclude_option_id: int | None = None) -> int:
    stmt = select(func.count(ReadingQuestionOption.id)).where(
        ReadingQuestionOption.question_id == question_id,
        ReadingQuestionOption.is_correct.is_(True),
    )
    if exclude_option_id is not None:
        stmt = stmt.where(ReadingQuestionOption.id != exclude_option_id)
    return int((await db.execute(stmt)).scalar_one())


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
    block_type = await _resolve_question_block_type(db, question_id)
    ensure_options_supported(module="reading", block_type=block_type)
    validate_option_text(payload.option_text)

    if payload.is_correct:
        ensure_single_correct_option_limit(await _count_correct_options(db, question_id=question_id))

    row = ReadingQuestionOption(
        question_id=question_id,
        option_text=payload.option_text.strip(),
        is_correct=payload.is_correct,
        order=payload.order,
    )
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

    block_type = await _resolve_question_block_type(db, row.question_id)
    ensure_options_supported(module="reading", block_type=block_type)
    validate_option_text(payload.option_text)

    if payload.is_correct:
        ensure_single_correct_option_limit(
            await _count_correct_options(db, question_id=row.question_id, exclude_option_id=row.id)
        )

    row.option_text = payload.option_text.strip()
    row.is_correct = payload.is_correct
    row.order = payload.order

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
    block_type = await _resolve_question_block_type(db, question_id)
    ensure_answers_supported(module="reading", block_type=block_type)
    validate_correct_answer_text(payload.correct_answers)

    row = ReadingQuestionAnswer(
        question_id=question_id,
        correct_answers=payload.correct_answers.strip(),
    )
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

    block_type = await _resolve_question_block_type(db, row.question_id)
    ensure_answers_supported(module="reading", block_type=block_type)
    validate_correct_answer_text(payload.correct_answers)

    row.correct_answers = payload.correct_answers.strip()
    await log_admin_action(db, admin_user, "update", "reading_answer", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_reading_answer(db: AsyncSession, admin_user: User, *, answer_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ReadingQuestionAnswer, answer_id, "reading_answer_not_found", "Answer not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "reading_answer", answer_id)
    await db.commit()
    return {"message": "deleted"}
