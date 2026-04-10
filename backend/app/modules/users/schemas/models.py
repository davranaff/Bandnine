from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.db.models import RoleEnum


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: RoleEnum
    is_active: bool
    verified_at: datetime | None


class UserMeUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=120)
    last_name: str | None = Field(default=None, min_length=1, max_length=120)


class ChangePasswordIn(BaseModel):
    old_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class UserProfilePublic(BaseModel):
    id: int
    user_id: int
    date_of_birth: date | None
    country: str
    native_language: str
    target_band_score: Decimal


class UserProfileUpdate(BaseModel):
    date_of_birth: date | None = None
    country: str | None = None
    native_language: str | None = None
    target_band_score: Decimal | None = None
