from fastapi import APIRouter

from .reading_passages_blocks import router as reading_passages_blocks_router
from .reading_questions import router as reading_questions_router
from .reading_tests import router as reading_tests_router

router = APIRouter()
router.include_router(reading_tests_router)
router.include_router(reading_passages_blocks_router)
router.include_router(reading_questions_router)
