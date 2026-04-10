from __future__ import annotations

from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ApiError

T = TypeVar("T")


async def get_or_404(
    db: AsyncSession,
    model: type[T],
    entity_id: int,
    code: str,
    message: str,
) -> T:
    entity = await db.get(model, entity_id)
    if entity is None:
        raise ApiError(code=code, message=message, status_code=404)
    return entity
