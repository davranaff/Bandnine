from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ConfirmToken, PasswordResetToken, User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    normalized_email = email.lower()
    return (await db.execute(select(User).where(func.lower(User.email) == normalized_email))).scalar_one_or_none()


async def get_confirm_token_by_hash(db: AsyncSession, token_hash: str) -> ConfirmToken | None:
    return (await db.execute(select(ConfirmToken).where(ConfirmToken.token_hash == token_hash).limit(1))).scalar_one_or_none()


async def get_password_reset_token_by_hash(db: AsyncSession, token_hash: str) -> PasswordResetToken | None:
    return (
        await db.execute(select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash).limit(1))
    ).scalar_one_or_none()

