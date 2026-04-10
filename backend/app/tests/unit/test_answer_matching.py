from app.modules.exams.service import _match_answer


def test_match_answer_trim_and_case_insensitive() -> None:
    assert _match_answer("  AnSwEr ", ["answer", "something"])
    assert _match_answer("YES", ["no", "yes"])
    assert not _match_answer("incorrect", ["correct"])
