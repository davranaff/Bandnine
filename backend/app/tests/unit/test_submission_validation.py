from dataclasses import dataclass, field

import pytest

from app.core.errors import ApiError
from app.modules.exams.services.validation import (
    validate_listening_submit_payload,
    validate_reading_submit_payload,
    validate_writing_submit_payload,
)


@dataclass
class FakeOption:
    option_text: str


@dataclass
class FakeBlock:
    block_type: str
    description: str = ""
    table_completion: str | None = None
    question_heading: str | None = None


@dataclass
class FakeQuestion:
    id: int
    question_block: FakeBlock
    options: list[FakeOption] = field(default_factory=list)


def _reasons(exc: ApiError) -> set[str]:
    assert isinstance(exc.details, list)
    return {str(item["reason"]) for item in exc.details}


def test_submit_validation_missing_answers() -> None:
    q1 = FakeQuestion(id=1, question_block=FakeBlock(block_type="short_answers"))
    q2 = FakeQuestion(id=2, question_block=FakeBlock(block_type="short_answers"))

    with pytest.raises(ApiError) as exc_info:
        validate_reading_submit_payload(
            [{"id": 1, "value": "answer"}],
            question_index={1: q1, 2: q2},
        )

    assert exc_info.value.code == "invalid_exam_submission"
    assert "missing_question_answer" in _reasons(exc_info.value)


def test_submit_validation_unknown_and_duplicate_question_ids() -> None:
    q1 = FakeQuestion(id=1, question_block=FakeBlock(block_type="short_answers"))

    with pytest.raises(ApiError) as exc_info:
        validate_reading_submit_payload(
            [
                {"id": 1, "value": "a"},
                {"id": 1, "value": "b"},
                {"id": 999, "value": "x"},
            ],
            question_index={1: q1},
        )

    reasons = _reasons(exc_info.value)
    assert "duplicate_question_id" in reasons
    assert "unknown_question_id" in reasons


def test_submit_validation_invalid_single_choice_value() -> None:
    question = FakeQuestion(
        id=1,
        question_block=FakeBlock(block_type="true_false_ng"),
        options=[FakeOption("True"), FakeOption("False"), FakeOption("Not Given")],
    )

    with pytest.raises(ApiError) as exc_info:
        validate_reading_submit_payload(
            [{"id": 1, "value": "Maybe"}],
            question_index={1: question},
        )

    assert "invalid_option_value" in _reasons(exc_info.value)


def test_submit_validation_max_words_exceeded() -> None:
    question = FakeQuestion(
        id=10,
        question_block=FakeBlock(
            block_type="table_completion",
            description="Choose NO MORE THAN TWO WORDS",
            table_completion="Field A | Field B",
        ),
    )

    with pytest.raises(ApiError) as exc_info:
        validate_listening_submit_payload(
            [{"id": 10, "value": "three words total"}],
            question_index={10: question},
        )

    assert "max_words_exceeded" in _reasons(exc_info.value)


def test_writing_submit_validation_empty_and_missing_parts() -> None:
    with pytest.raises(ApiError) as exc_info:
        validate_writing_submit_payload(
            [{"part_id": 1, "essay": "   "}],
            part_ids={1, 2},
        )

    reasons = _reasons(exc_info.value)
    assert "empty_essay" in reasons
    assert "missing_part_essay" in reasons
