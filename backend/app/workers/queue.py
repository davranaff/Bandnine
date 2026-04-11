import logging

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings

logger = logging.getLogger(__name__)


async def _enqueue(job_name: str, *args, max_tries: int = 3) -> None:
    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await redis.enqueue_job(job_name, *args, _max_tries=max_tries)
    finally:
        await redis.close()


async def enqueue_table_parse(kind: str, block_id: int) -> None:
    await _enqueue("parse_table_completion", kind, block_id, max_tries=3)


async def enqueue_writing_evaluation(exam_part_id: int) -> None:
    await _enqueue("evaluate_writing_exam_part", exam_part_id, max_tries=3)
