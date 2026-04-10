import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import ApiError
from app.db.models import RefreshToken, RoleEnum, User
from app.db.session import get_db

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


def _utc_now_for_value(value: datetime | None) -> datetime:
    now = datetime.now(UTC)
    if value is not None and value.tzinfo is None:
        return now.replace(tzinfo=None)
    return now


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def sha256_token(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_random_token(length: int = 48) -> str:
    return secrets.token_urlsafe(length)


def _create_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    to_encode = payload.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "type": "access",
        "role": user.role.value,
    }
    return _create_token(payload, timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(user: User, jti: str | None = None) -> tuple[str, str, datetime]:
    token_id = jti or str(uuid.uuid4())
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "jti": token_id,
        "role": user.role.value,
    }
    token = _create_token(payload, timedelta(days=settings.refresh_token_expire_days))
    return token, token_id, expires_at


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ApiError(code="invalid_token", message="Invalid token", status_code=401) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(code="unauthorized", message="Missing bearer token", status_code=401)

    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise ApiError(code="invalid_token", message="Invalid access token", status_code=401)

    user_id = payload.get("sub")
    user = await db.get(User, int(user_id)) if user_id and str(user_id).isdigit() else None
    if not user or not user.is_active:
        raise ApiError(code="unauthorized", message="User is not authenticated", status_code=401)
    return user


def require_roles(*roles: RoleEnum):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ApiError(code="forbidden", message="Insufficient role", status_code=403)
        return user

    return dependency


async def resolve_refresh_token(
    refresh_token: str,
    db: AsyncSession,
    check_revoked: bool = True,
) -> tuple[dict[str, Any], User, RefreshToken]:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise ApiError(code="invalid_token", message="Invalid refresh token", status_code=401)

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub or not str(sub).isdigit():
        raise ApiError(code="invalid_token", message="Malformed refresh token", status_code=401)

    token_row = (
        await db.execute(
            select(RefreshToken).where(RefreshToken.jti == str(jti), RefreshToken.user_id == int(sub))
        )
    ).scalar_one_or_none()

    if not token_row:
        raise ApiError(code="invalid_token", message="Refresh token not found", status_code=401)

    if check_revoked and token_row.revoked_at is not None:
        raise ApiError(code="invalid_token", message="Refresh token revoked", status_code=401)

    if token_row.expires_at < _utc_now_for_value(token_row.expires_at):
        raise ApiError(code="invalid_token", message="Refresh token expired", status_code=401)

    if token_row.token_hash != sha256_token(refresh_token):
        raise ApiError(code="invalid_token", message="Refresh token mismatch", status_code=401)

    user = await db.get(User, token_row.user_id)
    if not user or not user.is_active:
        raise ApiError(code="unauthorized", message="Inactive user", status_code=401)

    return payload, user, token_row
