from app.modules.exams.score import reading_band_score


def test_reading_band_score_edges() -> None:
    assert reading_band_score(39) == 9.0
    assert reading_band_score(37) == 8.5
    assert reading_band_score(35) == 8.0
    assert reading_band_score(30) == 7.0
    assert reading_band_score(23) == 6.0
    assert reading_band_score(13) == 4.5
    assert reading_band_score(4) == 2.5
    assert reading_band_score(0) == 0.0
