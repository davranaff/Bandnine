from fastapi import APIRouter

from .listening_blocks import router as listening_blocks_router
from .listening_questions import router as listening_questions_router
from .listening_tests_parts import router as listening_tests_parts_router

router = APIRouter()
router.include_router(listening_tests_parts_router)
router.include_router(listening_blocks_router)
router.include_router(listening_questions_router)
