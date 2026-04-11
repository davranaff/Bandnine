from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage
from app.db.session import get_db
from app.modules.lessons import services

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/categories", response_model=CursorPage)
async def list_categories(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CursorPage:
    return await services.list_categories(db, offset=offset, limit=limit)


@router.get("/categories/{slug}/lessons", response_model=CursorPage)
async def list_lessons_by_category(
    slug: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CursorPage:
    return await services.list_lessons_by_category(
        db,
        slug=slug,
        offset=offset,
        limit=limit,
    )
