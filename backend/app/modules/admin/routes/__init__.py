from .exams import router as exams_router
from .lessons import router as lessons_router
from .listening import router as listening_router
from .reading import router as reading_router
from .writing import router as writing_router

__all__ = [
    "reading_router",
    "listening_router",
    "writing_router",
    "exams_router",
    "lessons_router",
]
