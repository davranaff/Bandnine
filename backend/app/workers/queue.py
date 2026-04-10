import logging

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings

logger = logging.getLogger(__name__)


async def enqueue_table_parse(kind: str, block_id: int) -> None:
    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await redis.enqueue_job("parse_table_completion", kind, block_id, _max_tries=3)
    finally:
        await redis.close()
