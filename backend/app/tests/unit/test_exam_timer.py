from datetime import UTC, datetime, timedelta

from app.db.models import FinishReasonEnum
from app.modules.exams.services.core import (
    _calculate_elapsed_seconds,
    _calculate_time_spent_seconds,
    _resolve_finish_reason,
)


def test_calculate_elapsed_seconds_returns_positive_seconds() -> None:
    started_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    finished_at = started_at + timedelta(seconds=75)

    assert _calculate_elapsed_seconds(started_at, finished_at) == 75


def test_calculate_time_spent_seconds_returns_raw_elapsed_without_cap() -> None:
    started_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    finished_at = started_at + timedelta(seconds=400)

    assert _calculate_time_spent_seconds(started_at, finished_at) == 400


def test_calculate_time_spent_seconds_handles_missing_start() -> None:
    finished_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)

    assert _calculate_time_spent_seconds(None, finished_at) is None


def test_resolve_finish_reason_uses_seconds_boundary() -> None:
    assert _resolve_finish_reason(elapsed_seconds=59, limit_seconds=60) == FinishReasonEnum.completed
    assert _resolve_finish_reason(elapsed_seconds=60, limit_seconds=60) == FinishReasonEnum.time_is_up
    assert _resolve_finish_reason(elapsed_seconds=65, limit_seconds=60) == FinishReasonEnum.time_is_up
