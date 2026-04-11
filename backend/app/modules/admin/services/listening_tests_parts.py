from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_admin_action
from app.core.pagination import CursorPage, paginate_query, serialize_page
from app.db.models import ListeningPart, ListeningTest, User
from app.modules.admin import repository
from app.modules.admin.schemas import ListeningPartIn, ListeningTestIn


async def list_listening_tests(
    db: AsyncSession,
    *,
    offset: int,
    limit: int,
) -> CursorPage:
    rows = await paginate_query(db, select(ListeningTest), ListeningTest.id, limit, offset)
    return serialize_page(
        rows,
        serializer=lambda row: {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "time_limit": row.time_limit,
            "is_active": row.is_active,
            "voice_url": row.voice_url,
        },
        limit=limit,
        offset=offset,
    )


async def create_listening_test(db: AsyncSession, admin_user: User, payload: ListeningTestIn) -> dict[str, Any]:
    row = ListeningTest(**payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "listening_test", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_listening_test(
    db: AsyncSession,
    admin_user: User,
    *,
    test_id: int,
    payload: ListeningTestIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ListeningTest, test_id, "listening_test_not_found", "Listening test not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    await log_admin_action(db, admin_user, "update", "listening_test", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_listening_test(db: AsyncSession, admin_user: User, *, test_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ListeningTest, test_id, "listening_test_not_found", "Listening test not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "listening_test", test_id)
    await db.commit()
    return {"message": "deleted"}


async def create_listening_part(
    db: AsyncSession,
    admin_user: User,
    *,
    test_id: int,
    payload: ListeningPartIn,
) -> dict[str, Any]:
    await repository.get_or_404(db, ListeningTest, test_id, "listening_test_not_found", "Listening test not found")
    row = ListeningPart(test_id=test_id, **payload.model_dump())
    db.add(row)
    await db.flush()
    await log_admin_action(db, admin_user, "create", "listening_part", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def patch_listening_part(
    db: AsyncSession,
    admin_user: User,
    *,
    part_id: int,
    payload: ListeningPartIn,
) -> dict[str, Any]:
    row = await repository.get_or_404(db, ListeningPart, part_id, "listening_part_not_found", "Part not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    await log_admin_action(db, admin_user, "update", "listening_part", row.id, payload.model_dump())
    await db.commit()
    return {"id": row.id}


async def delete_listening_part(db: AsyncSession, admin_user: User, *, part_id: int) -> dict[str, str]:
    row = await repository.get_or_404(db, ListeningPart, part_id, "listening_part_not_found", "Part not found")
    await db.delete(row)
    await log_admin_action(db, admin_user, "delete", "listening_part", part_id)
    await db.commit()
    return {"message": "deleted"}
