from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.base import Base


def import_models() -> None:
    # Ensure model metadata is registered.
    from app.db import models  # noqa: F401


async def create_all(engine: AsyncEngine) -> None:
    import_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all(engine: AsyncEngine) -> None:
    import_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
