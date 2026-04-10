import pytest
from arq import Retry

from app.db.models import ParseStatusEnum, ReadingPassage, ReadingQuestionBlock, ReadingTest
from app.db.session import SessionLocal
from app.workers import tasks


@pytest.mark.asyncio
async def test_table_parse_pending_to_done(db_session, monkeypatch):
    test = ReadingTest(title="RT", description="D", time_limit=60, total_questions=0, is_active=True)
    db_session.add(test)
    await db_session.flush()

    passage = ReadingPassage(test_id=test.id, title="P", content="C", passage_number=1)
    db_session.add(passage)
    await db_session.flush()

    block = ReadingQuestionBlock(
        passage_id=passage.id,
        title="B",
        description="D",
        block_type="table_completion",
        order=1,
        table_completion="<table></table>",
        parse_status=ParseStatusEnum.pending,
    )
    db_session.add(block)
    await db_session.commit()

    async def fake_parse(content: str) -> dict:
        return {"header": ["A"], "rows": [["B"]]}

    monkeypatch.setattr(tasks, "_parse_table_to_json", fake_parse)
    await tasks.parse_table_completion({"job_try": 1}, "reading", block.id)

    async with SessionLocal() as verify_db:
        refreshed = await verify_db.get(ReadingQuestionBlock, block.id)
        assert refreshed is not None
        assert refreshed.parse_status == ParseStatusEnum.done
        assert refreshed.table_json == {"header": ["A"], "rows": [["B"]]}


@pytest.mark.asyncio
async def test_table_parse_failed_with_retries(db_session, monkeypatch):
    test = ReadingTest(title="RT2", description="D", time_limit=60, total_questions=0, is_active=True)
    db_session.add(test)
    await db_session.flush()

    passage = ReadingPassage(test_id=test.id, title="P2", content="C2", passage_number=1)
    db_session.add(passage)
    await db_session.flush()

    block = ReadingQuestionBlock(
        passage_id=passage.id,
        title="B2",
        description="D2",
        block_type="table_completion",
        order=1,
        table_completion="bad",
        parse_status=ParseStatusEnum.pending,
    )
    db_session.add(block)
    await db_session.commit()

    async def fail_parse(content: str) -> dict:
        raise RuntimeError("parse error")

    monkeypatch.setattr(tasks, "_parse_table_to_json", fail_parse)

    with pytest.raises(Retry):
        await tasks.parse_table_completion({"job_try": 1}, "reading", block.id)

    await tasks.parse_table_completion({"job_try": 3}, "reading", block.id)

    async with SessionLocal() as verify_db:
        refreshed = await verify_db.get(ReadingQuestionBlock, block.id)
        assert refreshed is not None
        assert refreshed.parse_status == ParseStatusEnum.failed
        assert "parse error" in (refreshed.parse_error or "")
