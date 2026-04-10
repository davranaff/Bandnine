from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage
from app.core.security import get_current_user, require_roles
from app.db.models import RoleEnum, User
from app.db.session import get_db
from app.modules.users import services
from app.modules.users.schemas import ChangePasswordIn, UserMeUpdate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return await services.get_me(current_user)


@router.patch("/me", response_model=UserPublic)
async def patch_me(
    payload: UserMeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    return await services.patch_me(
        db,
        current_user,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )


@router.put("/me/password")
async def change_password(
    payload: ChangePasswordIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    await services.change_password(
        db,
        current_user,
        old_password=payload.old_password,
        new_password=payload.new_password,
    )
    return {"message": "Password changed"}


@router.get("", response_model=CursorPage)
async def list_users(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(RoleEnum.admin)),
) -> CursorPage:
    return await services.list_users(
        db,
        cursor=cursor,
        limit=limit,
        search=search,
    )
