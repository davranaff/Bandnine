from __future__ import annotations

from typing import Any

from app.core.errors import ApiError
from app.modules.listening.services.core import (
    LISTENING_DROPDOWN_BLOCK_TYPES,
    LISTENING_INLINE_TEXT_BLOCK_TYPES,
    LISTENING_RADIO_BLOCK_TYPES,
    LISTENING_TABLE_BLOCK_TYPES,
)
from app.modules.reading.services.core import (
    READING_DROPDOWN_BLOCK_TYPES,
    READING_INLINE_TEXT_BLOCK_TYPES,
    READING_RADIO_BLOCK_TYPES,
    READING_TABLE_BLOCK_TYPES,
)

READING_SINGLE_CHOICE_BLOCK_TYPES = READING_DROPDOWN_BLOCK_TYPES | READING_RADIO_BLOCK_TYPES
LISTENING_SINGLE_CHOICE_BLOCK_TYPES = LISTENING_DROPDOWN_BLOCK_TYPES | LISTENING_RADIO_BLOCK_TYPES

READING_VALID_BLOCK_TYPES = (
    READING_SINGLE_CHOICE_BLOCK_TYPES | READING_INLINE_TEXT_BLOCK_TYPES | READING_TABLE_BLOCK_TYPES
)
LISTENING_VALID_BLOCK_TYPES = (
    LISTENING_SINGLE_CHOICE_BLOCK_TYPES | LISTENING_INLINE_TEXT_BLOCK_TYPES | LISTENING_TABLE_BLOCK_TYPES
)

READING_REQUIRED_FIELDS_BY_BLOCK_TYPE: dict[str, tuple[str, ...]] = {
    "matching_headings": ("list_of_headings",),
    "note_completion": ("question_heading",),
    "table_completion": ("table_completion",),
    "flow_chart_completion": ("flow_chart_completion",),
}
LISTENING_REQUIRED_FIELDS_BY_BLOCK_TYPE: dict[str, tuple[str, ...]] = {
    "table_completion": ("table_completion",),
}


def _raise_invalid_admin_payload(details: list[dict[str, Any]]) -> None:
    raise ApiError(
        code="invalid_admin_payload",
        message="Admin payload is invalid",
        status_code=400,
        details=details,
    )


def _validate_block_payload(
    *,
    payload: Any,
    valid_block_types: set[str],
    required_fields: dict[str, tuple[str, ...]],
) -> None:
    details: list[dict[str, Any]] = []

    block_type = str(payload.block_type).strip()
    if block_type not in valid_block_types:
        details.append(
            {
                "field": "block_type",
                "reason": "invalid_block_type",
                "value": payload.block_type,
            }
        )

    for field_name in required_fields.get(block_type, ()):  # pragma: no branch
        raw_value = getattr(payload, field_name, None)
        if not isinstance(raw_value, str) or not raw_value.strip():
            details.append(
                {
                    "field": field_name,
                    "reason": "missing_required_field",
                    "value": raw_value,
                }
            )

    if details:
        _raise_invalid_admin_payload(details)


def validate_reading_block_payload(payload: Any) -> None:
    _validate_block_payload(
        payload=payload,
        valid_block_types=READING_VALID_BLOCK_TYPES,
        required_fields=READING_REQUIRED_FIELDS_BY_BLOCK_TYPE,
    )


def validate_listening_block_payload(payload: Any) -> None:
    _validate_block_payload(
        payload=payload,
        valid_block_types=LISTENING_VALID_BLOCK_TYPES,
        required_fields=LISTENING_REQUIRED_FIELDS_BY_BLOCK_TYPE,
    )


def validate_option_text(option_text: str) -> None:
    if option_text.strip():
        return
    _raise_invalid_admin_payload(
        [
            {
                "field": "option_text",
                "reason": "empty_option_text",
                "value": option_text,
            }
        ]
    )


def validate_correct_answer_text(correct_answers: str) -> None:
    if correct_answers.strip():
        return
    _raise_invalid_admin_payload(
        [
            {
                "field": "correct_answers",
                "reason": "empty_correct_answer",
                "value": correct_answers,
            }
        ]
    )


def ensure_options_supported(*, module: str, block_type: str) -> None:
    if module == "reading" and block_type in READING_SINGLE_CHOICE_BLOCK_TYPES:
        return
    if module == "listening" and block_type in LISTENING_SINGLE_CHOICE_BLOCK_TYPES:
        return
    _raise_invalid_admin_payload(
        [
            {
                "field": "block_type",
                "reason": "options_not_supported_for_block_type",
                "value": block_type,
            }
        ]
    )


def ensure_answers_supported(*, module: str, block_type: str) -> None:
    if module == "reading" and block_type not in READING_SINGLE_CHOICE_BLOCK_TYPES:
        return
    if module == "listening" and block_type not in LISTENING_SINGLE_CHOICE_BLOCK_TYPES:
        return
    _raise_invalid_admin_payload(
        [
            {
                "field": "block_type",
                "reason": "answers_not_supported_for_block_type",
                "value": block_type,
            }
        ]
    )


def ensure_single_correct_option_limit(correct_options_count: int) -> None:
    if correct_options_count < 1:
        return
    _raise_invalid_admin_payload(
        [
            {
                "field": "is_correct",
                "reason": "single_choice_allows_only_one_correct_option",
                "value": True,
            }
        ]
    )
