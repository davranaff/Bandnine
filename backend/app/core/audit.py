from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AdminAuditLog, User


async def log_admin_action(
    db: AsyncSession,
    admin_user: User,
    action: str,
    entity: str,
    entity_id: int | None = None,
    payload: Any = None,
) -> None:
    serialized_payload = jsonable_encoder(payload) if payload is not None else None
    db.add(
        AdminAuditLog(
            admin_user_id=admin_user.id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            payload=serialized_payload,
        )
    )
