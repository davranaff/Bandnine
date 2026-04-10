def reading_band_score(raw_score: int) -> float:
    if raw_score >= 39:
        return 9.0
    if raw_score >= 37:
        return 8.5
    if raw_score >= 35:
        return 8.0
    if raw_score >= 33:
        return 7.5
    if raw_score >= 30:
        return 7.0
    if raw_score >= 27:
        return 6.5
    if raw_score >= 23:
        return 6.0
    if raw_score >= 19:
        return 5.5
    if raw_score >= 15:
        return 5.0
    if raw_score >= 13:
        return 4.5
    if raw_score >= 10:
        return 4.0
    if raw_score >= 8:
        return 3.5
    if raw_score >= 6:
        return 3.0
    if raw_score >= 4:
        return 2.5
    return 0.0
