import asyncio
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from app.core.errors import ApiError


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._bucket: dict[str, list[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = datetime.now(UTC)
        window_start = now - timedelta(seconds=window_seconds)

        async with self._lock:
            timestamps = self._bucket[key]
            timestamps[:] = [ts for ts in timestamps if ts >= window_start]
            if len(timestamps) >= limit:
                raise ApiError(
                    code="rate_limited",
                    message="Too many requests. Please try again later.",
                    status_code=429,
                )
            timestamps.append(now)


rate_limiter = InMemoryRateLimiter()
