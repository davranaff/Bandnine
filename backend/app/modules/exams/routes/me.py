from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.modules.exams import services
from app.modules.exams.schemas import ExamsMeOut

router = APIRouter()


@router.get("/me", response_model=ExamsMeOut)
async def get_my_exams(
    reading_cursor: str | None = Query(default=None),
    listening_cursor: str | None = Query(default=None),
    writing_cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExamsMeOut:
    return ExamsMeOut.model_validate(
        await services.get_my_exams(
            db,
            current_user,
            reading_cursor=reading_cursor,
            listening_cursor=listening_cursor,
            writing_cursor=writing_cursor,
            limit=limit,
        )
    )
