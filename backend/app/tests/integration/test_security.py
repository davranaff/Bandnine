from datetime import UTC, datetime

import pytest

from app.core.security import hash_password
from app.db.models import RoleEnum, User


async def _create_user(db_session, email: str, role: RoleEnum) -> None:
    db_session.add(
        User(
            email=email,
            password_hash=hash_password("Password123"),
            first_name="First",
            last_name="Last",
            role=role,
            is_active=True,
            verified_at=datetime.now(UTC),
        )
    )
    await db_session.commit()


@pytest.mark.asyncio
async def test_admin_guard_and_refresh_revocation(client, db_session):
    await _create_user(db_session, "admin@test.com", RoleEnum.admin)
    await _create_user(db_session, "student@test.com", RoleEnum.student)

    no_auth = await client.get("/api/v1/admin/reading/tests")
    assert no_auth.status_code == 401

    student_sign_in = await client.post(
        "/api/v1/auth/sign-in",
        json={"email": "student@test.com", "password": "Password123"},
    )
    student_access = student_sign_in.json()["tokens"]["access_token"]
    student_refresh = student_sign_in.json()["tokens"]["refresh_token"]

    forbidden = await client.get(
        "/api/v1/admin/reading/tests",
        headers={"Authorization": f"Bearer {student_access}"},
    )
    assert forbidden.status_code == 403

    sign_out = await client.post("/api/v1/auth/sign-out", json={"refresh_token": student_refresh})
    assert sign_out.status_code == 200

    refresh_after_logout = await client.post("/api/v1/auth/refresh", json={"refresh_token": student_refresh})
    assert refresh_after_logout.status_code == 401
