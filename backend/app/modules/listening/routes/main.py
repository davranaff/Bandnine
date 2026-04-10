from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage
from app.db.session import get_db
from app.modules.listening import services
from app.modules.listening.schemas import ListeningTestDetail

router = APIRouter(prefix="/listening", tags=["listening"])


@router.get("/tests", response_model=CursorPage)
async def list_tests(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CursorPage:
    return await services.list_listening_tests(db, cursor=cursor, limit=limit)


@router.get("/tests/{test_id}", response_model=ListeningTestDetail)
async def get_test(test_id: int, db: AsyncSession = Depends(get_db)) -> ListeningTestDetail:
    payload = await services.get_listening_test_detail(db, test_id)
    return ListeningTestDetail.model_validate(payload)
