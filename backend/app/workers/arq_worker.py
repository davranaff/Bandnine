from arq.connections import RedisSettings

from app.core.config import settings
from app.workers.tasks import evaluate_writing_exam_part, parse_table_completion


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [parse_table_completion, evaluate_writing_exam_part]
    max_jobs = 10
