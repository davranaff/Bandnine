from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage
from app.core.security import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.modules.profile import services
from app.modules.profile.schemas import (
    AnalyticsOut,
    DashboardOut,
    ProfileOut,
    ProfilePatchIn,
    ProgressIn,
    ProgressOut,
)

router = APIRouter(tags=["profile"])


@router.get("/profile", response_model=ProfileOut)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileOut:
    profile = await services.get_or_create_profile(db, current_user)
    return ProfileOut(
        id=profile.id,
        user_id=profile.user_id,
        date_of_birth=profile.date_of_birth,
        country=profile.country,
        native_language=profile.native_language,
        target_band_score=profile.target_band_score,
    )


@router.patch("/profile", response_model=ProfileOut)
async def patch_profile(
    payload: ProfilePatchIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileOut:
    clean_payload = payload.model_dump(exclude_none=True)
    return await services.patch_profile(db, current_user, clean_payload)


@router.get("/progress", response_model=CursorPage)
async def list_progress(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CursorPage:
    return await services.list_progress(db, current_user, offset, limit)


@router.post("/progress", response_model=ProgressOut)
async def create_progress(
    payload: ProgressIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressOut:
    return await services.create_progress(db, current_user, payload.model_dump())


@router.get("/analytics", response_model=AnalyticsOut)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalyticsOut:
    return await services.get_analytics(db, current_user)


@router.get("/dashboard", response_model=DashboardOut)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardOut:
    payload = await services.get_dashboard(db, current_user)
    return DashboardOut.model_validate(payload)
