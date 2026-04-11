from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select, asc
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class OffsetPage(BaseModel):
    items: list[Any]
    limit: int
    offset: int


# Backward-compatible alias for existing imports.
CursorPage = OffsetPage


def normalize_limit(limit: int) -> int:
    return max(1, min(limit, 100))


def normalize_offset(offset: int) -> int:
    return max(0, offset)


async def paginate_query(
    session: AsyncSession,
    stmt: Select,
    id_column,
    limit: int,
    offset: int,
) -> list[Any]:
    normalized_limit = normalize_limit(limit)
    normalized_offset = normalize_offset(offset)
    paged_stmt = stmt.order_by(asc(id_column)).offset(normalized_offset).limit(normalized_limit)
    return list((await session.execute(paged_stmt)).scalars().all())


def page_response(items: list[Any], limit: int, offset: int) -> OffsetPage:
    return OffsetPage(
        items=items,
        limit=normalize_limit(limit),
        offset=normalize_offset(offset),
    )


def serialize_page(
    items: Sequence[T],
    serializer: Callable[[T], Any],
    limit: int,
    offset: int,
) -> OffsetPage:
    return page_response(items=[serializer(item) for item in items], limit=limit, offset=offset)
