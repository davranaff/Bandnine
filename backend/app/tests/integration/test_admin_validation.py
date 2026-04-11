from datetime import UTC, datetime

import pytest

from app.core.security import hash_password
from app.db.models import RoleEnum, User


async def _create_admin(db_session, email: str) -> User:
    admin = User(
        email=email,
        password_hash=hash_password("Password123"),
        first_name="Admin",
        last_name="Validation",
        role=RoleEnum.admin,
        is_active=True,
        verified_at=datetime.now(UTC),
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


async def _admin_headers(client, email: str) -> dict[str, str]:
    sign_in = await client.post("/api/v1/auth/sign-in", json={"email": email, "password": "Password123"})
    assert sign_in.status_code == 200
    access = sign_in.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {access}"}


@pytest.mark.asyncio
async def test_admin_reading_validation_rules(client, db_session):
    admin = await _create_admin(db_session, "admin-reading-validation@example.com")
    headers = await _admin_headers(client, admin.email)

    reading_test = await client.post(
        "/api/v1/admin/reading/tests",
        headers=headers,
        json={"title": "Reading Admin", "description": "Desc", "time_limit": 3600, "is_active": True},
    )
    assert reading_test.status_code == 200
    test_id = reading_test.json()["id"]

    passage = await client.post(
        f"/api/v1/admin/reading/tests/{test_id}/passages",
        headers=headers,
        json={"title": "Passage", "content": "Content", "passage_number": 1},
    )
    assert passage.status_code == 200
    passage_id = passage.json()["id"]

    invalid_type = await client.post(
        f"/api/v1/admin/reading/passages/{passage_id}/blocks",
        headers=headers,
        json={"title": "Bad", "description": "Desc", "block_type": "unsupported", "order": 1},
    )
    assert invalid_type.status_code == 400
    assert invalid_type.json()["code"] == "invalid_admin_payload"

    invalid_required = await client.post(
        f"/api/v1/admin/reading/passages/{passage_id}/blocks",
        headers=headers,
        json={"title": "Table", "description": "Desc", "block_type": "table_completion", "order": 1},
    )
    assert invalid_required.status_code == 400
    reasons = {item["reason"] for item in invalid_required.json()["details"]}
    assert "missing_required_field" in reasons

    text_block = await client.post(
        f"/api/v1/admin/reading/passages/{passage_id}/blocks",
        headers=headers,
        json={"title": "Text", "description": "Desc", "block_type": "short_answers", "order": 2},
    )
    assert text_block.status_code == 200
    text_block_id = text_block.json()["id"]

    text_question = await client.post(
        f"/api/v1/admin/reading/blocks/{text_block_id}/questions",
        headers=headers,
        json={"question_text": "Q-text", "order": 1},
    )
    assert text_question.status_code == 200
    text_question_id = text_question.json()["id"]

    options_for_text = await client.post(
        f"/api/v1/admin/reading/questions/{text_question_id}/options",
        headers=headers,
        json={"option_text": "A", "is_correct": True, "order": 1},
    )
    assert options_for_text.status_code == 400
    reasons = {item["reason"] for item in options_for_text.json()["details"]}
    assert "options_not_supported_for_block_type" in reasons

    text_answer = await client.post(
        f"/api/v1/admin/reading/questions/{text_question_id}/answers",
        headers=headers,
        json={"correct_answers": "answer"},
    )
    assert text_answer.status_code == 200

    choice_block = await client.post(
        f"/api/v1/admin/reading/passages/{passage_id}/blocks",
        headers=headers,
        json={"title": "Choice", "description": "Desc", "block_type": "true_false_ng", "order": 3},
    )
    assert choice_block.status_code == 200
    choice_block_id = choice_block.json()["id"]

    choice_question = await client.post(
        f"/api/v1/admin/reading/blocks/{choice_block_id}/questions",
        headers=headers,
        json={"question_text": "Q-choice", "order": 1},
    )
    assert choice_question.status_code == 200
    choice_question_id = choice_question.json()["id"]

    answers_for_choice = await client.post(
        f"/api/v1/admin/reading/questions/{choice_question_id}/answers",
        headers=headers,
        json={"correct_answers": "True"},
    )
    assert answers_for_choice.status_code == 400
    reasons = {item["reason"] for item in answers_for_choice.json()["details"]}
    assert "answers_not_supported_for_block_type" in reasons

    first_correct = await client.post(
        f"/api/v1/admin/reading/questions/{choice_question_id}/options",
        headers=headers,
        json={"option_text": "True", "is_correct": True, "order": 1},
    )
    assert first_correct.status_code == 200

    second_correct = await client.post(
        f"/api/v1/admin/reading/questions/{choice_question_id}/options",
        headers=headers,
        json={"option_text": "False", "is_correct": True, "order": 2},
    )
    assert second_correct.status_code == 400
    reasons = {item["reason"] for item in second_correct.json()["details"]}
    assert "single_choice_allows_only_one_correct_option" in reasons


@pytest.mark.asyncio
async def test_admin_listening_validation_rules(client, db_session):
    admin = await _create_admin(db_session, "admin-listening-validation@example.com")
    headers = await _admin_headers(client, admin.email)

    listening_test = await client.post(
        "/api/v1/admin/listening/tests",
        headers=headers,
        json={
            "title": "Listening Admin",
            "description": "Desc",
            "time_limit": 2400,
            "is_active": True,
            "voice_url": "https://example.com/audio.mp3",
        },
    )
    assert listening_test.status_code == 200
    test_id = listening_test.json()["id"]

    part = await client.post(
        f"/api/v1/admin/listening/tests/{test_id}/parts",
        headers=headers,
        json={"title": "Part 1", "order": 1},
    )
    assert part.status_code == 200
    part_id = part.json()["id"]

    invalid_type = await client.post(
        f"/api/v1/admin/listening/parts/{part_id}/blocks",
        headers=headers,
        json={"title": "Bad", "description": "Desc", "block_type": "unsupported", "order": 1},
    )
    assert invalid_type.status_code == 400

    invalid_required = await client.post(
        f"/api/v1/admin/listening/parts/{part_id}/blocks",
        headers=headers,
        json={"title": "Table", "description": "Desc", "block_type": "table_completion", "order": 1},
    )
    assert invalid_required.status_code == 400
    reasons = {item["reason"] for item in invalid_required.json()["details"]}
    assert "missing_required_field" in reasons

    text_block = await client.post(
        f"/api/v1/admin/listening/parts/{part_id}/blocks",
        headers=headers,
        json={"title": "Text", "description": "Desc", "block_type": "short_answer", "order": 2},
    )
    assert text_block.status_code == 200
    text_block_id = text_block.json()["id"]

    text_question = await client.post(
        f"/api/v1/admin/listening/blocks/{text_block_id}/questions",
        headers=headers,
        json={"question_text": "Q-text", "order": 1},
    )
    assert text_question.status_code == 200
    text_question_id = text_question.json()["id"]

    options_for_text = await client.post(
        f"/api/v1/admin/listening/questions/{text_question_id}/options",
        headers=headers,
        json={"option_text": "A", "is_correct": True, "order": 1},
    )
    assert options_for_text.status_code == 400
    reasons = {item["reason"] for item in options_for_text.json()["details"]}
    assert "options_not_supported_for_block_type" in reasons

    text_answer = await client.post(
        f"/api/v1/admin/listening/questions/{text_question_id}/answers",
        headers=headers,
        json={"correct_answers": "answer"},
    )
    assert text_answer.status_code == 200

    choice_block = await client.post(
        f"/api/v1/admin/listening/parts/{part_id}/blocks",
        headers=headers,
        json={"title": "Choice", "description": "Desc", "block_type": "multiple_choice", "order": 3},
    )
    assert choice_block.status_code == 200
    choice_block_id = choice_block.json()["id"]

    choice_question = await client.post(
        f"/api/v1/admin/listening/blocks/{choice_block_id}/questions",
        headers=headers,
        json={"question_text": "Q-choice", "order": 1},
    )
    assert choice_question.status_code == 200
    choice_question_id = choice_question.json()["id"]

    answers_for_choice = await client.post(
        f"/api/v1/admin/listening/questions/{choice_question_id}/answers",
        headers=headers,
        json={"correct_answers": "A"},
    )
    assert answers_for_choice.status_code == 400
    reasons = {item["reason"] for item in answers_for_choice.json()["details"]}
    assert "answers_not_supported_for_block_type" in reasons

    first_correct = await client.post(
        f"/api/v1/admin/listening/questions/{choice_question_id}/options",
        headers=headers,
        json={"option_text": "A", "is_correct": True, "order": 1},
    )
    assert first_correct.status_code == 200

    second_correct = await client.post(
        f"/api/v1/admin/listening/questions/{choice_question_id}/options",
        headers=headers,
        json={"option_text": "B", "is_correct": True, "order": 2},
    )
    assert second_correct.status_code == 400
    reasons = {item["reason"] for item in second_correct.json()["details"]}
    assert "single_choice_allows_only_one_correct_option" in reasons
