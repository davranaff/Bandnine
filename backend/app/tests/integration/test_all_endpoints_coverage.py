from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.core.security import hash_password
from app.db.models import (
    ListeningPart,
    ListeningQuestion,
    ListeningQuestionAnswer,
    ListeningQuestionBlock,
    ListeningTest,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionAnswer,
    ReadingQuestionBlock,
    ReadingTest,
    RoleEnum,
    User,
    WritingPart,
    WritingTest,
)
from app.main import app

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


async def _create_active_user(db_session, email: str, role: RoleEnum, password: str = "Password123") -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name="Test",
        last_name="User",
        role=role,
        is_active=True,
        verified_at=datetime.now(UTC),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _sign_in(client, email: str, password: str = "Password123") -> dict[str, str]:
    response = await client.post("/api/v1/auth/sign-in", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    payload = response.json()["tokens"]
    return {
        "access": payload["access_token"],
        "refresh": payload["refresh_token"],
    }


@pytest.mark.asyncio
async def test_all_endpoints_are_covered(client, db_session):
    expected_ops = {
        (method.upper(), path)
        for path, payload in app.openapi()["paths"].items()
        for method in payload
        if method.upper() in HTTP_METHODS
    }
    called_ops: set[tuple[str, str]] = set()

    async def hit(
        method: str,
        op_path: str,
        real_path: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict | list | None = None,
        status_code: int = 200,
    ):
        response = await client.request(method, real_path, headers=headers, json=json)
        assert response.status_code == status_code, (
            f"{method} {real_path} expected {status_code} got {response.status_code}: {response.text}"
        )
        called_ops.add((method.upper(), op_path))
        return response

    # Health/readiness
    app.state.redis = SimpleNamespace(ping=AsyncMock(return_value=True))
    await hit("GET", "/health", "/health")
    await hit("GET", "/readiness", "/readiness")

    # Seed core users
    admin_user = await _create_active_user(db_session, "admin-coverage@example.com", RoleEnum.admin)
    student_user = await _create_active_user(db_session, "student-coverage@example.com", RoleEnum.student)

    admin_sign_in = await hit(
        "POST",
        "/api/v1/auth/sign-in",
        "/api/v1/auth/sign-in",
        json={"email": admin_user.email, "password": "Password123"},
    )
    admin_tokens_payload = admin_sign_in.json()["tokens"]
    admin_tokens = {
        "access": admin_tokens_payload["access_token"],
        "refresh": admin_tokens_payload["refresh_token"],
    }
    student_tokens = await _sign_in(client, student_user.email)

    admin_headers = {"Authorization": f"Bearer {admin_tokens['access']}"}
    student_headers = {"Authorization": f"Bearer {student_tokens['access']}"}

    # Auth flow coverage: sign-up, confirm, refresh, sign-out, reset-link, reset-password
    sign_up = await hit(
        "POST",
        "/api/v1/auth/sign-up",
        "/api/v1/auth/sign-up",
        status_code=201,
        json={
            "email": "flow-coverage@example.com",
            "password": "Password123",
            "first_name": "Flow",
            "last_name": "Coverage",
        },
    )
    confirm_token = sign_up.json()["debug_confirmation_token"]

    confirm = await hit(
        "POST",
        "/api/v1/auth/confirm",
        "/api/v1/auth/confirm",
        json={"token": confirm_token},
    )
    flow_refresh = confirm.json()["tokens"]["refresh_token"]

    await hit(
        "POST",
        "/api/v1/auth/refresh",
        "/api/v1/auth/refresh",
        json={"refresh_token": flow_refresh},
    )
    await hit(
        "POST",
        "/api/v1/auth/sign-out",
        "/api/v1/auth/sign-out",
        json={"refresh_token": flow_refresh},
    )

    reset_link = await hit(
        "POST",
        "/api/v1/auth/reset-link",
        "/api/v1/auth/reset-link",
        json={"email": "flow-coverage@example.com"},
    )
    reset_token = reset_link.json()["debug_reset_token"]
    await hit(
        "POST",
        "/api/v1/auth/reset-password",
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "password": "Password1234"},
    )

    # Users endpoints
    await hit("GET", "/api/v1/users/me", "/api/v1/users/me", headers=student_headers)
    await hit(
        "PATCH",
        "/api/v1/users/me",
        "/api/v1/users/me",
        headers=student_headers,
        json={"first_name": "Changed", "last_name": "Name"},
    )
    await hit(
        "PUT",
        "/api/v1/users/me/password",
        "/api/v1/users/me/password",
        headers=student_headers,
        json={"old_password": "Password123", "new_password": "Password123X"},
    )
    await hit("GET", "/api/v1/users", "/api/v1/users?search=student", headers=admin_headers)

    # Profile endpoints
    await hit("GET", "/api/v1/profile", "/api/v1/profile", headers=student_headers)
    await hit(
        "PATCH",
        "/api/v1/profile",
        "/api/v1/profile",
        headers=student_headers,
        json={"country": "UZ", "native_language": "uz"},
    )
    await hit(
        "POST",
        "/api/v1/progress",
        "/api/v1/progress",
        headers=student_headers,
        json={
            "band_score": "6.5",
            "correct_answers": 30,
            "total_questions": 40,
            "time_taken_seconds": 3100,
            "test_type": "reading",
        },
    )
    await hit("GET", "/api/v1/progress", "/api/v1/progress", headers=student_headers)
    await hit("GET", "/api/v1/analytics", "/api/v1/analytics", headers=student_headers)
    await hit("GET", "/api/v1/dashboard", "/api/v1/dashboard", headers=student_headers)

    # Admin reading CRUD chain
    await hit("GET", "/api/v1/admin/reading/tests", "/api/v1/admin/reading/tests", headers=admin_headers)
    reading_test_resp = await hit(
        "POST",
        "/api/v1/admin/reading/tests",
        "/api/v1/admin/reading/tests",
        headers=admin_headers,
        json={"title": "Admin Reading", "description": "Desc", "time_limit": 60, "is_active": True},
    )
    reading_test_id = reading_test_resp.json()["id"]
    await hit(
        "GET",
        "/api/v1/admin/reading/tests/{test_id}",
        f"/api/v1/admin/reading/tests/{reading_test_id}",
        headers=admin_headers,
    )
    await hit(
        "PATCH",
        "/api/v1/admin/reading/tests/{test_id}",
        f"/api/v1/admin/reading/tests/{reading_test_id}",
        headers=admin_headers,
        json={"title": "Admin Reading Updated", "description": "Desc", "time_limit": 65, "is_active": True},
    )
    reading_passage_resp = await hit(
        "POST",
        "/api/v1/admin/reading/tests/{test_id}/passages",
        f"/api/v1/admin/reading/tests/{reading_test_id}/passages",
        headers=admin_headers,
        json={"title": "Passage", "content": "Content", "passage_number": 1},
    )
    reading_passage_id = reading_passage_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/reading/passages/{passage_id}",
        f"/api/v1/admin/reading/passages/{reading_passage_id}",
        headers=admin_headers,
        json={"title": "Passage Upd", "content": "Content 2", "passage_number": 1},
    )
    reading_block_resp = await hit(
        "POST",
        "/api/v1/admin/reading/passages/{passage_id}/blocks",
        f"/api/v1/admin/reading/passages/{reading_passage_id}/blocks",
        headers=admin_headers,
        json={"title": "Block", "description": "Desc", "block_type": "short_answers", "order": 1},
    )
    reading_block_id = reading_block_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/reading/blocks/{block_id}",
        f"/api/v1/admin/reading/blocks/{reading_block_id}",
        headers=admin_headers,
        json={"title": "Block Upd", "description": "Desc 2", "block_type": "short_answers", "order": 1},
    )
    reading_question_resp = await hit(
        "POST",
        "/api/v1/admin/reading/blocks/{block_id}/questions",
        f"/api/v1/admin/reading/blocks/{reading_block_id}/questions",
        headers=admin_headers,
        json={"question_text": "Question", "order": 1},
    )
    reading_question_id = reading_question_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/reading/questions/{question_id}",
        f"/api/v1/admin/reading/questions/{reading_question_id}",
        headers=admin_headers,
        json={"question_text": "Question Upd", "order": 1},
    )
    reading_option_resp = await hit(
        "POST",
        "/api/v1/admin/reading/questions/{question_id}/options",
        f"/api/v1/admin/reading/questions/{reading_question_id}/options",
        headers=admin_headers,
        json={"option_text": "A", "is_correct": True, "order": 1},
    )
    reading_option_id = reading_option_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/reading/options/{option_id}",
        f"/api/v1/admin/reading/options/{reading_option_id}",
        headers=admin_headers,
        json={"option_text": "A1", "is_correct": True, "order": 1},
    )
    reading_answer_resp = await hit(
        "POST",
        "/api/v1/admin/reading/questions/{question_id}/answers",
        f"/api/v1/admin/reading/questions/{reading_question_id}/answers",
        headers=admin_headers,
        json={"correct_answers": "answer"},
    )
    reading_answer_id = reading_answer_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/reading/answers/{answer_id}",
        f"/api/v1/admin/reading/answers/{reading_answer_id}",
        headers=admin_headers,
        json={"correct_answers": "answer"},
    )

    # Admin listening CRUD chain
    await hit("GET", "/api/v1/admin/listening/tests", "/api/v1/admin/listening/tests", headers=admin_headers)
    listening_test_resp = await hit(
        "POST",
        "/api/v1/admin/listening/tests",
        "/api/v1/admin/listening/tests",
        headers=admin_headers,
        json={
            "title": "Admin Listening",
            "description": "Desc",
            "time_limit": 40,
            "is_active": True,
            "voice_url": "https://example.com/audio.mp3",
        },
    )
    listening_test_id = listening_test_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/listening/tests/{test_id}",
        f"/api/v1/admin/listening/tests/{listening_test_id}",
        headers=admin_headers,
        json={
            "title": "Admin Listening Updated",
            "description": "Desc",
            "time_limit": 45,
            "is_active": True,
            "voice_url": "https://example.com/audio2.mp3",
        },
    )
    listening_part_resp = await hit(
        "POST",
        "/api/v1/admin/listening/tests/{test_id}/parts",
        f"/api/v1/admin/listening/tests/{listening_test_id}/parts",
        headers=admin_headers,
        json={"title": "Part", "order": 1},
    )
    listening_part_id = listening_part_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/listening/parts/{part_id}",
        f"/api/v1/admin/listening/parts/{listening_part_id}",
        headers=admin_headers,
        json={"title": "Part Upd", "order": 1},
    )
    listening_block_resp = await hit(
        "POST",
        "/api/v1/admin/listening/parts/{part_id}/blocks",
        f"/api/v1/admin/listening/parts/{listening_part_id}/blocks",
        headers=admin_headers,
        json={"title": "Block", "description": "Desc", "block_type": "short_answer", "order": 1},
    )
    listening_block_id = listening_block_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/listening/blocks/{block_id}",
        f"/api/v1/admin/listening/blocks/{listening_block_id}",
        headers=admin_headers,
        json={"title": "Block Upd", "description": "Desc2", "block_type": "short_answer", "order": 1},
    )
    listening_question_resp = await hit(
        "POST",
        "/api/v1/admin/listening/blocks/{block_id}/questions",
        f"/api/v1/admin/listening/blocks/{listening_block_id}/questions",
        headers=admin_headers,
        json={"question_text": "Question", "order": 1},
    )
    listening_question_id = listening_question_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/listening/questions/{question_id}",
        f"/api/v1/admin/listening/questions/{listening_question_id}",
        headers=admin_headers,
        json={"question_text": "Question Upd", "order": 1},
    )
    listening_option_resp = await hit(
        "POST",
        "/api/v1/admin/listening/questions/{question_id}/options",
        f"/api/v1/admin/listening/questions/{listening_question_id}/options",
        headers=admin_headers,
        json={"option_text": "A", "is_correct": True, "order": 1},
    )
    listening_option_id = listening_option_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/listening/options/{option_id}",
        f"/api/v1/admin/listening/options/{listening_option_id}",
        headers=admin_headers,
        json={"option_text": "A1", "is_correct": True, "order": 1},
    )
    listening_answer_resp = await hit(
        "POST",
        "/api/v1/admin/listening/questions/{question_id}/answers",
        f"/api/v1/admin/listening/questions/{listening_question_id}/answers",
        headers=admin_headers,
        json={"correct_answers": "listen"},
    )
    listening_answer_id = listening_answer_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/listening/answers/{answer_id}",
        f"/api/v1/admin/listening/answers/{listening_answer_id}",
        headers=admin_headers,
        json={"correct_answers": "listen"},
    )

    # Admin writing CRUD chain
    await hit("GET", "/api/v1/admin/writing/tests", "/api/v1/admin/writing/tests", headers=admin_headers)
    writing_test_resp = await hit(
        "POST",
        "/api/v1/admin/writing/tests",
        "/api/v1/admin/writing/tests",
        headers=admin_headers,
        json={"title": "Admin Writing", "description": "Desc", "time_limit": 60, "is_active": True},
    )
    writing_test_id = writing_test_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/writing/tests/{test_id}",
        f"/api/v1/admin/writing/tests/{writing_test_id}",
        headers=admin_headers,
        json={"title": "Admin Writing Updated", "description": "Desc2", "time_limit": 65, "is_active": True},
    )
    writing_part_resp = await hit(
        "POST",
        "/api/v1/admin/writing/tests/{test_id}/parts",
        f"/api/v1/admin/writing/tests/{writing_test_id}/parts",
        headers=admin_headers,
        json={"order": 1, "task": "Write something", "image_url": None},
    )
    writing_part_id = writing_part_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/writing/parts/{part_id}",
        f"/api/v1/admin/writing/parts/{writing_part_id}",
        headers=admin_headers,
        json={"order": 1, "task": "Write better", "image_url": "https://example.com/img.png"},
    )

    # Admin lessons CRUD
    await hit("GET", "/api/v1/admin/lessons/categories", "/api/v1/admin/lessons/categories", headers=admin_headers)
    category_resp = await hit(
        "POST",
        "/api/v1/admin/lessons/categories",
        "/api/v1/admin/lessons/categories",
        headers=admin_headers,
        json={"title": "Grammar", "slug": "grammar"},
    )
    category_id = category_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/lessons/categories/{category_id}",
        f"/api/v1/admin/lessons/categories/{category_id}",
        headers=admin_headers,
        json={"title": "Grammar Updated", "slug": "grammar-updated"},
    )
    await hit("GET", "/api/v1/admin/lessons", "/api/v1/admin/lessons", headers=admin_headers)
    lesson_resp = await hit(
        "POST",
        "/api/v1/admin/lessons",
        "/api/v1/admin/lessons",
        headers=admin_headers,
        json={"category_id": category_id, "title": "Lesson", "video_link": "https://example.com/v1"},
    )
    lesson_id = lesson_resp.json()["id"]
    await hit(
        "PATCH",
        "/api/v1/admin/lessons/{lesson_id}",
        f"/api/v1/admin/lessons/{lesson_id}",
        headers=admin_headers,
        json={"category_id": category_id, "title": "Lesson Updated", "video_link": "https://example.com/v2"},
    )

    # Public lessons endpoints
    await hit("GET", "/api/v1/lessons/categories", "/api/v1/lessons/categories")
    await hit(
        "GET",
        "/api/v1/lessons/categories/{slug}/lessons",
        "/api/v1/lessons/categories/grammar-updated/lessons",
    )

    # Public reading/listening/writing endpoints on admin-created tests
    await hit("GET", "/api/v1/reading/tests", "/api/v1/reading/tests")
    await hit(
        "GET",
        "/api/v1/reading/tests/{test_id}",
        f"/api/v1/reading/tests/{reading_test_id}",
    )
    await hit("GET", "/api/v1/listening/tests", "/api/v1/listening/tests")
    await hit(
        "GET",
        "/api/v1/listening/tests/{test_id}",
        f"/api/v1/listening/tests/{listening_test_id}",
    )
    await hit("GET", "/api/v1/writing/tests", "/api/v1/writing/tests")
    await hit(
        "GET",
        "/api/v1/writing/tests/{test_id}",
        f"/api/v1/writing/tests/{writing_test_id}",
    )

    # Separate exam seed for stable exam flows (independent from admin CRUD delete chain)
    read_exam_test = ReadingTest(title="Exam Reading", description="Desc", time_limit=60, total_questions=1, is_active=True)
    db_session.add(read_exam_test)
    await db_session.flush()
    read_exam_passage = ReadingPassage(test_id=read_exam_test.id, title="P", content="C", passage_number=1)
    db_session.add(read_exam_passage)
    await db_session.flush()
    read_exam_block = ReadingQuestionBlock(
        passage_id=read_exam_passage.id,
        title="B",
        description="D",
        block_type="short_answers",
        order=1,
    )
    db_session.add(read_exam_block)
    await db_session.flush()
    read_exam_question = ReadingQuestion(question_block_id=read_exam_block.id, question_text="Q", order=1)
    db_session.add(read_exam_question)
    await db_session.flush()
    db_session.add(ReadingQuestionAnswer(question_id=read_exam_question.id, correct_answers="answer"))

    listen_exam_test = ListeningTest(
        title="Exam Listening",
        description="Desc",
        time_limit=30,
        total_questions=1,
        is_active=True,
        voice_url="https://example.com/e.mp3",
    )
    db_session.add(listen_exam_test)
    await db_session.flush()
    listen_exam_part = ListeningPart(test_id=listen_exam_test.id, title="Part", order=1)
    db_session.add(listen_exam_part)
    await db_session.flush()
    listen_exam_block = ListeningQuestionBlock(
        part_id=listen_exam_part.id,
        title="Block",
        description="Desc",
        block_type="short_answer",
        order=1,
    )
    db_session.add(listen_exam_block)
    await db_session.flush()
    listen_exam_question = ListeningQuestion(question_block_id=listen_exam_block.id, question_text="Q", order=1)
    db_session.add(listen_exam_question)
    await db_session.flush()
    db_session.add(ListeningQuestionAnswer(question_id=listen_exam_question.id, correct_answers="listen"))

    write_exam_test = WritingTest(title="Exam Writing", description="Desc", time_limit=60, is_active=True)
    db_session.add(write_exam_test)
    await db_session.flush()
    write_exam_part = WritingPart(test_id=write_exam_test.id, order=1, task="Write essay")
    db_session.add(write_exam_part)
    await db_session.commit()

    # Exams endpoints
    reading_exam_resp = await hit(
        "POST",
        "/api/v1/exams/reading",
        "/api/v1/exams/reading",
        headers=student_headers,
        json={"test_id": read_exam_test.id},
    )
    reading_exam_id = reading_exam_resp.json()["id"]
    await hit(
        "POST",
        "/api/v1/exams/reading/{exam_id}/start",
        f"/api/v1/exams/reading/{reading_exam_id}/start",
        headers=student_headers,
    )
    await hit(
        "POST",
        "/api/v1/exams/reading/{exam_id}/submit",
        f"/api/v1/exams/reading/{reading_exam_id}/submit",
        headers=student_headers,
        json=[{"id": read_exam_question.id, "value": "answer"}],
    )

    listening_exam_resp = await hit(
        "POST",
        "/api/v1/exams/listening",
        "/api/v1/exams/listening",
        headers=student_headers,
        json={"test_id": listen_exam_test.id},
    )
    listening_exam_id = listening_exam_resp.json()["id"]
    await hit(
        "POST",
        "/api/v1/exams/listening/{exam_id}/start",
        f"/api/v1/exams/listening/{listening_exam_id}/start",
        headers=student_headers,
    )
    await hit(
        "POST",
        "/api/v1/exams/listening/{exam_id}/submit",
        f"/api/v1/exams/listening/{listening_exam_id}/submit",
        headers=student_headers,
        json=[{"id": listen_exam_question.id, "value": "listen"}],
    )

    writing_exam_resp = await hit(
        "POST",
        "/api/v1/exams/writing",
        "/api/v1/exams/writing",
        headers=student_headers,
        json={"test_id": write_exam_test.id},
    )
    writing_exam_id = writing_exam_resp.json()["id"]
    await hit(
        "POST",
        "/api/v1/exams/writing/{exam_id}/start",
        f"/api/v1/exams/writing/{writing_exam_id}/start",
        headers=student_headers,
    )
    writing_submit_resp = await hit(
        "POST",
        "/api/v1/exams/writing/{exam_id}/submit",
        f"/api/v1/exams/writing/{writing_exam_id}/submit",
        headers=student_headers,
        json=[{"part_id": write_exam_part.id, "essay": "Essay text"}],
    )
    writing_exam_part_id = writing_submit_resp.json()["answers"][0]["id"]

    await hit("GET", "/api/v1/exams/me", "/api/v1/exams/me", headers=student_headers)

    # Admin exam endpoints
    await hit("GET", "/api/v1/admin/exams/{kind}", "/api/v1/admin/exams/reading", headers=admin_headers)
    await hit("GET", "/api/v1/admin/exams/{kind}", "/api/v1/admin/exams/listening", headers=admin_headers)
    await hit("GET", "/api/v1/admin/exams/{kind}", "/api/v1/admin/exams/writing", headers=admin_headers)
    await hit(
        "GET",
        "/api/v1/admin/exams/{kind}/{exam_id}",
        f"/api/v1/admin/exams/reading/{reading_exam_id}",
        headers=admin_headers,
    )
    await hit(
        "GET",
        "/api/v1/admin/exams/{kind}/{exam_id}",
        f"/api/v1/admin/exams/listening/{listening_exam_id}",
        headers=admin_headers,
    )
    await hit(
        "GET",
        "/api/v1/admin/exams/{kind}/{exam_id}",
        f"/api/v1/admin/exams/writing/{writing_exam_id}",
        headers=admin_headers,
    )
    await hit(
        "PATCH",
        "/api/v1/admin/exams/writing/parts/{exam_part_id}/review",
        f"/api/v1/admin/exams/writing/parts/{writing_exam_part_id}/review",
        headers=admin_headers,
        json={"is_checked": True, "corrections": "Good", "score": "7.0"},
    )

    # Admin delete endpoints coverage
    await hit(
        "DELETE",
        "/api/v1/admin/reading/answers/{answer_id}",
        f"/api/v1/admin/reading/answers/{reading_answer_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/reading/options/{option_id}",
        f"/api/v1/admin/reading/options/{reading_option_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/reading/questions/{question_id}",
        f"/api/v1/admin/reading/questions/{reading_question_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/reading/blocks/{block_id}",
        f"/api/v1/admin/reading/blocks/{reading_block_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/reading/passages/{passage_id}",
        f"/api/v1/admin/reading/passages/{reading_passage_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/reading/tests/{test_id}",
        f"/api/v1/admin/reading/tests/{reading_test_id}",
        headers=admin_headers,
    )

    await hit(
        "DELETE",
        "/api/v1/admin/listening/answers/{answer_id}",
        f"/api/v1/admin/listening/answers/{listening_answer_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/listening/options/{option_id}",
        f"/api/v1/admin/listening/options/{listening_option_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/listening/questions/{question_id}",
        f"/api/v1/admin/listening/questions/{listening_question_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/listening/blocks/{block_id}",
        f"/api/v1/admin/listening/blocks/{listening_block_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/listening/parts/{part_id}",
        f"/api/v1/admin/listening/parts/{listening_part_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/listening/tests/{test_id}",
        f"/api/v1/admin/listening/tests/{listening_test_id}",
        headers=admin_headers,
    )

    await hit(
        "DELETE",
        "/api/v1/admin/writing/parts/{part_id}",
        f"/api/v1/admin/writing/parts/{writing_part_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/writing/tests/{test_id}",
        f"/api/v1/admin/writing/tests/{writing_test_id}",
        headers=admin_headers,
    )

    await hit(
        "DELETE",
        "/api/v1/admin/lessons/{lesson_id}",
        f"/api/v1/admin/lessons/{lesson_id}",
        headers=admin_headers,
    )
    await hit(
        "DELETE",
        "/api/v1/admin/lessons/categories/{category_id}",
        f"/api/v1/admin/lessons/categories/{category_id}",
        headers=admin_headers,
    )

    missing = expected_ops - called_ops
    extra = called_ops - expected_ops

    assert not missing, f"Missing endpoint coverage for: {sorted(missing)}"
    assert not extra, f"Unknown/extra called operations: {sorted(extra)}"
