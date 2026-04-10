from fastapi import APIRouter

from app.modules.admin.api import router as admin_router
from app.modules.auth.api import router as auth_router
from app.modules.exams.api import router as exams_router
from app.modules.lessons.api import router as lessons_router
from app.modules.listening.api import router as listening_router
from app.modules.profile.api import router as profile_router
from app.modules.reading.api import router as reading_router
from app.modules.users.api import router as users_router
from app.modules.writing.api import router as writing_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(reading_router)
api_router.include_router(listening_router)
api_router.include_router(writing_router)
api_router.include_router(exams_router)
api_router.include_router(profile_router)
api_router.include_router(lessons_router)
api_router.include_router(admin_router)
