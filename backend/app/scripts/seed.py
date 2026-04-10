from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sqlalchemy import func, select

from app.core.security import hash_password
from app.db.models import Category, Lesson, RoleEnum, User
from app.db.session import SessionLocal


async def seed_roles_and_users() -> None:
    async with SessionLocal() as db:
        admin = (await db.execute(select(User).where(func.lower(User.email) == "admin@example.com"))).scalar_one_or_none()
        if admin is None:
            admin = User(
                email="admin@example.com",
                password_hash=hash_password("Admin12345"),
                first_name="System",
                last_name="Admin",
                role=RoleEnum.admin,
                is_active=True,
                verified_at=datetime.now(UTC),
            )
            db.add(admin)

        student = (await db.execute(select(User).where(func.lower(User.email) == "student@example.com"))).scalar_one_or_none()
        if student is None:
            student = User(
                email="student@example.com",
                password_hash=hash_password("Student12345"),
                first_name="Sample",
                last_name="Student",
                role=RoleEnum.student,
                is_active=True,
                verified_at=datetime.now(UTC),
            )
            db.add(student)

        await db.commit()


async def seed_lessons() -> None:
    async with SessionLocal() as db:
        categories = [
            ("Reading Lessons", "reading-lessons"),
            ("Listening Lessons", "listening-lessons"),
            ("Writing Lessons", "writing-lessons"),
            ("Speaking Lessons", "speaking-lessons"),
        ]

        for title, slug in categories:
            category = (await db.execute(select(Category).where(Category.slug == slug))).scalar_one_or_none()
            if category is None:
                category = Category(title=title, slug=slug)
                db.add(category)
                await db.flush()

                db.add(
                    Lesson(
                        category_id=category.id,
                        title=f"Intro to {title}",
                        video_link="https://www.youtube.com/embed/dQw4w9WgXcQ",
                    )
                )

        await db.commit()


async def main() -> None:
    await seed_roles_and_users()
    await seed_lessons()


if __name__ == "__main__":
    asyncio.run(main())
