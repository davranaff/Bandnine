from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ApiError
from app.core.pagination import CursorPage, serialize_page
from app.core.security import hash_password, verify_password
from app.db.models import User
from app.modules.users import repository
from app.modules.users.schemas import UserPublic


def user_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        verified_at=user.verified_at,
    )


async def get_me(current_user: User) -> UserPublic:
    return user_public(current_user)


async def patch_me(
    db: AsyncSession,
    current_user: User,
    *,
    first_name: str | None,
    last_name: str | None,
) -> UserPublic:
    if first_name is not None:
        current_user.first_name = first_name
    if last_name is not None:
        current_user.last_name = last_name

    await db.commit()
    await db.refresh(current_user)
    return user_public(current_user)


async def change_password(
    db: AsyncSession,
    current_user: User,
    *,
    old_password: str,
    new_password: str,
) -> None:
    if not verify_password(old_password, current_user.password_hash):
        raise ApiError(code="invalid_old_password", message="Incorrect old password", status_code=400)
    current_user.password_hash = hash_password(new_password)
    await db.commit()


async def list_users(
    db: AsyncSession,
    *,
    offset: int,
    limit: int,
    search: str | None,
) -> CursorPage:
    items = await repository.list_active_users(
        db,
        offset=offset,
        limit=limit,
        search=search,
    )
    return serialize_page(
        items,
        serializer=lambda user: user_public(user).model_dump(),
        limit=limit,
        offset=offset,
    )

