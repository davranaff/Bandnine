from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage
from app.db.session import get_db
from app.modules.writing import services
from app.modules.writing.schemas import WritingTestDetail

router = APIRouter(prefix="/writing", tags=["writing"])


@router.get("/tests", response_model=CursorPage)
async def list_tests(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CursorPage:
    return await services.list_writing_tests(db, cursor=cursor, limit=limit)


@router.get("/tests/{test_id}", response_model=WritingTestDetail)
async def get_test(test_id: int, db: AsyncSession = Depends(get_db)) -> WritingTestDetail:
    payload = await services.get_writing_test_detail(db, test_id)
    return WritingTestDetail.model_validate(payload)
