from __future__ import annotations

import re
from typing import Any

from app.core.errors import ApiError
from app.db.models import ListeningQuestion, ReadingQuestion
from app.modules.listening.services.core import _build_answer_spec as build_listening_answer_spec
from app.modules.reading.services.core import _build_answer_spec as build_reading_answer_spec

_WORDS_RE = re.compile(r"\S+")


def _raise_invalid_submission(details: list[dict[str, Any]]) -> None:
    raise ApiError(
        code="invalid_exam_submission",
        message="Exam submission payload is invalid",
        status_code=400,
        details=details,
    )


def _count_words(value: str) -> int:
    return len(_WORDS_RE.findall(value))


def _validate_choice_or_text_submission(
    answers: list[dict[str, Any]],
    *,
    question_index: dict[int, ReadingQuestion | ListeningQuestion],
    spec_builder: Any,
) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    normalized_answers: list[dict[str, Any]] = []

    expected_ids = set(question_index.keys())
    submitted_known_ids: set[int] = set()
    seen_ids: set[int] = set()

    for idx, item in enumerate(answers):
        field_prefix = f"answers[{idx}]"

        question_id = int(item["id"])
        raw_value = item.get("value", "")
        value = str(raw_value).strip()

        if question_id in seen_ids:
            details.append(
                {
                    "field": f"{field_prefix}.id",
                    "reason": "duplicate_question_id",
                    "value": question_id,
                }
            )
        seen_ids.add(question_id)

        question = question_index.get(question_id)
        if question is None:
            details.append(
                {
                    "field": f"{field_prefix}.id",
                    "reason": "unknown_question_id",
                    "value": question_id,
                }
            )
            continue
        submitted_known_ids.add(question_id)

        answer_spec = spec_builder(question.question_block)
        if answer_spec["answer_type"] == "single_choice":
            allowed_values = {
                str(option.option_text).strip().lower()
                for option in question.options
                if str(option.option_text).strip()
            }
            if value.lower() not in allowed_values:
                details.append(
                    {
                        "field": f"{field_prefix}.value",
                        "reason": "invalid_option_value",
                        "value": raw_value,
                    }
                )
        else:
            max_words = answer_spec.get("max_words")
            if max_words is not None and _count_words(value) > int(max_words):
                details.append(
                    {
                        "field": f"{field_prefix}.value",
                        "reason": "max_words_exceeded",
                        "value": raw_value,
                    }
                )

        normalized_answers.append(
            {
                "id": question_id,
                "value": value,
            }
        )

    missing_ids = sorted(expected_ids - submitted_known_ids)
    for missing_id in missing_ids:
        details.append(
            {
                "field": "answers",
                "reason": "missing_question_answer",
                "value": missing_id,
            }
        )

    if details:
        _raise_invalid_submission(details)

    return normalized_answers


def validate_reading_submit_payload(
    answers: list[dict[str, Any]],
    *,
    question_index: dict[int, ReadingQuestion],
) -> list[dict[str, Any]]:
    return _validate_choice_or_text_submission(
        answers,
        question_index=question_index,
        spec_builder=build_reading_answer_spec,
    )


def validate_listening_submit_payload(
    answers: list[dict[str, Any]],
    *,
    question_index: dict[int, ListeningQuestion],
) -> list[dict[str, Any]]:
    return _validate_choice_or_text_submission(
        answers,
        question_index=question_index,
        spec_builder=build_listening_answer_spec,
    )


def validate_writing_submit_payload(
    parts_payload: list[dict[str, Any]],
    *,
    part_ids: set[int],
) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    normalized_parts: list[dict[str, Any]] = []

    seen_ids: set[int] = set()
    submitted_known_ids: set[int] = set()

    for idx, item in enumerate(parts_payload):
        field_prefix = f"parts[{idx}]"
        part_id = int(item["part_id"])
        raw_essay = item.get("essay", "")
        essay = str(raw_essay).strip()

        if part_id in seen_ids:
            details.append(
                {
                    "field": f"{field_prefix}.part_id",
                    "reason": "duplicate_part_id",
                    "value": part_id,
                }
            )
        seen_ids.add(part_id)

        if part_id not in part_ids:
            details.append(
                {
                    "field": f"{field_prefix}.part_id",
                    "reason": "unknown_part_id",
                    "value": part_id,
                }
            )
            continue
        submitted_known_ids.add(part_id)

        if not essay:
            details.append(
                {
                    "field": f"{field_prefix}.essay",
                    "reason": "empty_essay",
                    "value": raw_essay,
                }
            )

        normalized_parts.append(
            {
                "part_id": part_id,
                "essay": essay,
            }
        )

    missing_ids = sorted(part_ids - submitted_known_ids)
    for missing_id in missing_ids:
        details.append(
            {
                "field": "parts",
                "reason": "missing_part_essay",
                "value": missing_id,
            }
        )

    if details:
        _raise_invalid_submission(details)

    return normalized_parts
