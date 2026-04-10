import base64
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select, asc
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class CursorPage(BaseModel):
    items: list[Any]
    next_cursor: str | None
    limit: int


def encode_cursor(value: int) -> str:
    return base64.urlsafe_b64encode(str(value).encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: str | None) -> int | None:
    if not cursor:
        return None
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        return int(raw)
    except Exception:
        return None


async def paginate_query(
    session: AsyncSession,
    stmt: Select,
    id_column,
    limit: int,
    cursor: str | None,
) -> tuple[Sequence[Any], str | None]:
    limit = max(1, min(limit, 100))
    cursor_value = decode_cursor(cursor)
    if cursor_value is not None:
        stmt = stmt.where(id_column > cursor_value)

    stmt = stmt.order_by(asc(id_column)).limit(limit + 1)
    rows = list((await session.execute(stmt)).scalars().all())

    next_cursor = None
    if len(rows) > limit:
        last_id = getattr(rows[limit - 1], "id")
        next_cursor = encode_cursor(last_id)
        rows = rows[:limit]

    return rows, next_cursor


def page_response(items: list[Any], next_cursor: str | None, limit: int) -> CursorPage:
    return CursorPage(items=items, next_cursor=next_cursor, limit=limit)


def serialize_page(
    items: Sequence[T],
    serializer: Callable[[T], Any],
    next_cursor: str | None,
    limit: int,
) -> CursorPage:
    return page_response(items=[serializer(item) for item in items], next_cursor=next_cursor, limit=limit)
