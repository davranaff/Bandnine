from fastapi import APIRouter

from app.modules.admin.routes import (
    exams_router,
    lessons_router,
    listening_router,
    reading_router,
    writing_router,
)

router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(reading_router)
router.include_router(listening_router)
router.include_router(writing_router)
router.include_router(exams_router)
router.include_router(lessons_router)
