from __future__ import annotations

import json
import logging

from arq import Retry
from openai import AsyncOpenAI
from sqlalchemy import select

from app.core.config import settings
from app.db.models import ListeningQuestionBlock, ParseStatusEnum, ReadingQuestionBlock
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


async def _parse_table_to_json(content: str) -> dict:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "developer",
                "content": "Return only valid JSON object with keys header and rows.",
            },
            {"role": "user", "content": content},
        ],
        temperature=0,
    )
    payload = response.choices[0].message.content or "{}"
    return json.loads(payload)


async def parse_table_completion(ctx: dict, kind: str, block_id: int) -> None:
    job_try = int(ctx.get("job_try", 1))

    async with SessionLocal() as db:
        model = ReadingQuestionBlock if kind == "reading" else ListeningQuestionBlock
        block = (await db.execute(select(model).where(model.id == block_id))).scalar_one_or_none()
        if block is None:
            logger.warning("Parse skipped, block not found", extra={"kind": kind, "block_id": block_id})
            return

        try:
            block.parse_status = ParseStatusEnum.pending
            await db.flush()

            result = await _parse_table_to_json(block.table_completion or "")
            block.table_json = result
            block.parse_status = ParseStatusEnum.done
            block.parse_error = None
            await db.commit()
        except Exception as exc:  # noqa: BLE001
            block.parse_error = str(exc)
            if job_try < 3:
                block.parse_status = ParseStatusEnum.pending
                await db.commit()
                raise Retry(defer=2**job_try) from exc

            block.parse_status = ParseStatusEnum.failed
            await db.commit()
            logger.exception("Table parse failed", extra={"kind": kind, "block_id": block_id})
