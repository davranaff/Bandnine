"""initial schema

Revision ID: 0001_initial
Revises: None
Create Date: 2026-04-10 00:00:00
"""

from collections.abc import Sequence

from alembic import op
from app.db.base import Base
from app.db.init_db import import_models

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    import_models()
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    import_models()
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
