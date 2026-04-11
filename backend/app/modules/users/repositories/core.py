from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import paginate_query
from app.db.models import User


async def list_active_users(
    db: AsyncSession,
    *,
    offset: int,
    limit: int,
    search: str | None,
) -> list[User]:
    stmt = select(User).where(User.is_active.is_(True))
    if search:
        q = f"%{search.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(User.first_name).like(q),
                func.lower(User.last_name).like(q),
                func.lower(User.email).like(q),
            )
        )
    return await paginate_query(db, stmt, User.id, limit, offset)

