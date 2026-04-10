from datetime import UTC, datetime

import pytest

from app.core.security import hash_password
from app.db.models import (
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionAnswer,
    ReadingQuestionBlock,
    ReadingQuestionOption,
    ReadingTest,
    RoleEnum,
    User,
)


async def _create_user(db_session, email: str) -> User:
    user = User(
        email=email,
        password_hash=hash_password("Password123"),
        first_name="Test",
        last_name="User",
        role=RoleEnum.student,
        is_active=True,
        verified_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_exam_start_submit_idempotent_and_ownership(client, db_session):
    user1 = await _create_user(db_session, "u1@example.com")
    user2 = await _create_user(db_session, "u2@example.com")

    reading_test = ReadingTest(title="R1", description="Desc", time_limit=60, total_questions=1, is_active=True)
    db_session.add(reading_test)
    await db_session.flush()

    passage = ReadingPassage(test_id=reading_test.id, title="P1", content="Text", passage_number=1)
    db_session.add(passage)
    await db_session.flush()

    block = ReadingQuestionBlock(
        passage_id=passage.id,
        title="B1",
        description="D",
        block_type="short_answers",
        order=1,
    )
    db_session.add(block)
    await db_session.flush()

    question = ReadingQuestion(question_block_id=block.id, question_text="Q1", order=1)
    db_session.add(question)
    await db_session.flush()

    db_session.add(ReadingQuestionAnswer(question_id=question.id, correct_answers="answer"))
    db_session.add(ReadingQuestionOption(question_id=question.id, option_text="answer", is_correct=True, order=1))
    await db_session.commit()

    sign_in_u1 = await client.post(
        "/api/v1/auth/sign-in", json={"email": user1.email, "password": "Password123"}
    )
    assert sign_in_u1.status_code == 200
    token_u1 = sign_in_u1.json()["tokens"]["access_token"]

    sign_in_u2 = await client.post(
        "/api/v1/auth/sign-in", json={"email": user2.email, "password": "Password123"}
    )
    assert sign_in_u2.status_code == 200
    token_u2 = sign_in_u2.json()["tokens"]["access_token"]

    create_exam = await client.post(
        "/api/v1/exams/reading",
        headers={"Authorization": f"Bearer {token_u1}"},
        json={"test_id": reading_test.id},
    )
    assert create_exam.status_code == 200
    exam_id = create_exam.json()["id"]

    start_once = await client.post(
        f"/api/v1/exams/reading/{exam_id}/start",
        headers={"Authorization": f"Bearer {token_u1}"},
    )
    assert start_once.status_code == 200
    start_twice = await client.post(
        f"/api/v1/exams/reading/{exam_id}/start",
        headers={"Authorization": f"Bearer {token_u1}"},
    )
    assert start_twice.status_code == 200

    forbidden_start = await client.post(
        f"/api/v1/exams/reading/{exam_id}/start",
        headers={"Authorization": f"Bearer {token_u2}"},
    )
    assert forbidden_start.status_code == 403

    submit_once = await client.post(
        f"/api/v1/exams/reading/{exam_id}/submit",
        headers={"Authorization": f"Bearer {token_u1}"},
        json=[{"id": question.id, "value": " Answer "}],
    )
    assert submit_once.status_code == 200
    assert submit_once.json()["correct_answers"] == 1

    submit_twice = await client.post(
        f"/api/v1/exams/reading/{exam_id}/submit",
        headers={"Authorization": f"Bearer {token_u1}"},
        json=[{"id": question.id, "value": "Wrong"}],
    )
    assert submit_twice.status_code == 200
    assert submit_twice.json()["correct_answers"] == 1
