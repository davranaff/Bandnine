from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
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
from app.modules.admin.services.validation import (
    ensure_answers_supported,
    ensure_options_supported,
    ensure_single_correct_option_limit,
    validate_correct_answer_text,
    validate_option_text,
)


async def _resolve_question_block_type(db: AsyncSession, question_id: int) -> str:
    question = await repository.get_or_404(db, ListeningQuestion, question_id, "listening_question_not_found", "Question not found")
    block = await repository.get_or_404(
        db,
        ListeningQuestionBlock,
        question.question_block_id,
        "listening_block_not_found",
        "Block not found",
    )
    return block.block_type


async def _count_correct_options(db: AsyncSession, *, question_id: int, exclude_option_id: int | None = None) -> int:
    stmt = select(func.count(ListeningQuestionOption.id)).where(
        ListeningQuestionOption.question_id == question_id,
        ListeningQuestionOption.is_correct.is_(True),
    )
    if exclude_option_id is not None:
        stmt = stmt.where(ListeningQuestionOption.id != exclude_option_id)
    return int((await db.execute(stmt)).scalar_one())


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
    block_type = await _resolve_question_block_type(db, question_id)
    ensure_options_supported(module="listening", block_type=block_type)
    validate_option_text(payload.option_text)

    if payload.is_correct:
        ensure_single_correct_option_limit(await _count_correct_options(db, question_id=question_id))

    row = ListeningQuestionOption(
        question_id=question_id,
        option_text=payload.option_text.strip(),
        is_correct=payload.is_correct,
        order=payload.order,
    )
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

    block_type = await _resolve_question_block_type(db, row.question_id)
    ensure_options_supported(module="listening", block_type=block_type)
    validate_option_text(payload.option_text)

    if payload.is_correct:
        ensure_single_correct_option_limit(
            await _count_correct_options(db, question_id=row.question_id, exclude_option_id=row.id)
        )

    row.option_text = payload.option_text.strip()
    row.is_correct = payload.is_correct
    row.order = payload.order

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
    block_type = await _resolve_question_block_type(db, question_id)
    ensure_answers_supported(module="listening", block_type=block_type)
    validate_correct_answer_text(payload.correct_answers)

    row = ListeningQuestionAnswer(
        question_id=question_id,
        correct_answers=payload.correct_answers.strip(),
    )
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

    block_type = await _resolve_question_block_type(db, row.question_id)
    ensure_answers_supported(module="listening", block_type=block_type)
    validate_correct_answer_text(payload.correct_answers)

    row.correct_answers = payload.correct_answers.strip()
    await log_admin_action(db, admin_user, "update", "listening_answer", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_listening_answer(db: AsyncSession, admin_user: User, *, answer_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ListeningQuestionAnswer, answer_id, "listening_answer_not_found", "Answer not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "listening_answer", answer_id)
    await db.commit()
    return {"message": "deleted"}
