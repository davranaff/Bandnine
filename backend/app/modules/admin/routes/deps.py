from fastapi import Depends

from app.core.security import require_roles
from app.db.models import RoleEnum


def admin_dependency():
    return Depends(require_roles(RoleEnum.admin))
