from __future__ import annotations

import enum
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class RoleEnum(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    accountant = "accountant"
    student = "student"
    user = "user"


class ProgressTestTypeEnum(str, enum.Enum):
    reading = "reading"
    listening = "listening"
    writing = "writing"
    speaking = "speaking"


class ParseStatusEnum(str, enum.Enum):
    pending = "pending"
    done = "done"
    failed = "failed"


class FinishReasonEnum(str, enum.Enum):
    completed = "completed"
    left = "left"
    time_is_up = "time_is_up"


role_enum = Enum(RoleEnum, name="role_enum", native_enum=False)
progress_test_type_enum = Enum(ProgressTestTypeEnum, name="progress_test_type_enum", native_enum=False)
parse_status_enum = Enum(ParseStatusEnum, name="parse_status_enum", native_enum=False)
finish_reason_enum = Enum(FinishReasonEnum, name="finish_reason_enum", native_enum=False)


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(role_enum, default=RoleEnum.user, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    profile: Mapped[UserProfile | None] = relationship(back_populates="user", uselist=False)
    analytics: Mapped[UserAnalytics | None] = relationship(back_populates="user", uselist=False)
    progress_entries: Mapped[list[UserProgress]] = relationship(back_populates="user")


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    date_of_birth: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    native_language: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    target_band_score: Mapped[Decimal] = mapped_column(Numeric(3, 1), default=Decimal("6.0"), nullable=False)

    user: Mapped[User] = relationship(back_populates="profile")


class UserProgress(TimestampMixin, Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    test_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    band_score: Mapped[Decimal] = mapped_column(Numeric(3, 1), nullable=False)
    correct_answers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_questions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_taken_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    test_type: Mapped[ProgressTestTypeEnum] = mapped_column(progress_test_type_enum, nullable=False)

    user: Mapped[User] = relationship(back_populates="progress_entries")


class UserAnalytics(TimestampMixin, Base):
    __tablename__ = "user_analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    total_tests_taken: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_band_score: Mapped[Decimal] = mapped_column(Numeric(3, 1), default=Decimal("0.0"), nullable=False)
    best_band_score: Mapped[Decimal] = mapped_column(Numeric(3, 1), default=Decimal("0.0"), nullable=False)
    total_study_time_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_test_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="analytics")


class RefreshToken(TimestampMixin, Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ConfirmToken(TimestampMixin, Base):
    __tablename__ = "confirm_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PasswordResetToken(TimestampMixin, Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Category(TimestampMixin, Base):
    __tablename__ = "lesson_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    lessons: Mapped[list[Lesson]] = relationship(back_populates="category", cascade="all, delete-orphan")


class Lesson(TimestampMixin, Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("lesson_categories.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    video_link: Mapped[str] = mapped_column(String(500), nullable=False)

    category: Mapped[Category] = relationship(back_populates="lessons")


class ReadingTest(TimestampMixin, Base):
    __tablename__ = "reading_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    time_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    passages: Mapped[list[ReadingPassage]] = relationship(
        back_populates="test", cascade="all, delete-orphan"
    )


class ReadingPassage(TimestampMixin, Base):
    __tablename__ = "reading_passages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("reading_tests.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    passage_number: Mapped[int] = mapped_column(Integer, nullable=False)

    test: Mapped[ReadingTest] = relationship(back_populates="passages")
    question_blocks: Mapped[list[ReadingQuestionBlock]] = relationship(
        back_populates="passage", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("test_id", "passage_number", name="uq_reading_passage_order"),
    )


class ReadingQuestionBlock(TimestampMixin, Base):
    __tablename__ = "reading_question_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passage_id: Mapped[int] = mapped_column(
        ForeignKey("reading_passages.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    block_type: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    question_heading: Mapped[str | None] = mapped_column(String(255), nullable=True)
    list_of_headings: Mapped[str | None] = mapped_column(Text, nullable=True)

    table_completion: Mapped[str | None] = mapped_column(Text, nullable=True)
    flow_chart_completion: Mapped[str | None] = mapped_column(Text, nullable=True)
    table_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    parse_status: Mapped[ParseStatusEnum] = mapped_column(
        parse_status_enum, default=ParseStatusEnum.done, nullable=False
    )
    parse_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    passage: Mapped[ReadingPassage] = relationship(back_populates="question_blocks")
    questions: Mapped[list[ReadingQuestion]] = relationship(
        back_populates="question_block", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("passage_id", "order", name="uq_reading_block_order"),
    )


class ReadingQuestion(TimestampMixin, Base):
    __tablename__ = "reading_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_block_id: Mapped[int] = mapped_column(
        ForeignKey("reading_question_blocks.id", ondelete="CASCADE"), index=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    question_block: Mapped[ReadingQuestionBlock] = relationship(back_populates="questions")
    answers: Mapped[list[ReadingQuestionAnswer]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
    options: Mapped[list[ReadingQuestionOption]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("question_block_id", "order", name="uq_reading_question_order"),
    )


class ReadingQuestionAnswer(TimestampMixin, Base):
    __tablename__ = "reading_question_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("reading_questions.id", ondelete="CASCADE"), index=True
    )
    correct_answers: Mapped[str] = mapped_column(String(255), nullable=False)

    question: Mapped[ReadingQuestion] = relationship(back_populates="answers")


class ReadingQuestionOption(TimestampMixin, Base):
    __tablename__ = "reading_question_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("reading_questions.id", ondelete="CASCADE"), index=True
    )
    option_text: Mapped[str] = mapped_column(String(500), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    question: Mapped[ReadingQuestion] = relationship(back_populates="options")


class ListeningTest(TimestampMixin, Base):
    __tablename__ = "listening_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    time_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    voice_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    parts: Mapped[list[ListeningPart]] = relationship(back_populates="test", cascade="all, delete-orphan")


class ListeningPart(TimestampMixin, Base):
    __tablename__ = "listening_parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("listening_tests.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    test: Mapped[ListeningTest] = relationship(back_populates="parts")
    question_blocks: Mapped[list[ListeningQuestionBlock]] = relationship(
        back_populates="part", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("test_id", "order", name="uq_listening_part_order"),
    )


class ListeningQuestionBlock(TimestampMixin, Base):
    __tablename__ = "listening_question_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("listening_parts.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    block_type: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    table_completion: Mapped[str | None] = mapped_column(Text, nullable=True)
    table_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    parse_status: Mapped[ParseStatusEnum] = mapped_column(
        parse_status_enum, default=ParseStatusEnum.done, nullable=False
    )
    parse_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    part: Mapped[ListeningPart] = relationship(back_populates="question_blocks")
    questions: Mapped[list[ListeningQuestion]] = relationship(
        back_populates="question_block", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("part_id", "order", name="uq_listening_block_order"),
    )


class ListeningQuestion(TimestampMixin, Base):
    __tablename__ = "listening_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_block_id: Mapped[int] = mapped_column(
        ForeignKey("listening_question_blocks.id", ondelete="CASCADE"), index=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    question_block: Mapped[ListeningQuestionBlock] = relationship(back_populates="questions")
    answers: Mapped[list[ListeningQuestionAnswer]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
    options: Mapped[list[ListeningQuestionOption]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("question_block_id", "order", name="uq_listening_question_order"),
    )


class ListeningQuestionAnswer(TimestampMixin, Base):
    __tablename__ = "listening_question_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("listening_questions.id", ondelete="CASCADE"), index=True
    )
    correct_answers: Mapped[str] = mapped_column(String(255), nullable=False)

    question: Mapped[ListeningQuestion] = relationship(back_populates="answers")


class ListeningQuestionOption(TimestampMixin, Base):
    __tablename__ = "listening_question_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("listening_questions.id", ondelete="CASCADE"), index=True
    )
    option_text: Mapped[str] = mapped_column(String(500), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    question: Mapped[ListeningQuestion] = relationship(back_populates="options")


class WritingTest(TimestampMixin, Base):
    __tablename__ = "writing_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    time_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    writing_parts: Mapped[list[WritingPart]] = relationship(
        back_populates="test", cascade="all, delete-orphan"
    )


class WritingPart(TimestampMixin, Base):
    __tablename__ = "writing_parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("writing_tests.id", ondelete="CASCADE"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    test: Mapped[WritingTest] = relationship(back_populates="writing_parts")

    __table_args__ = (
        UniqueConstraint("test_id", "order", name="uq_writing_part_order"),
    )


class ReadingExam(TimestampMixin, Base):
    __tablename__ = "reading_exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    reading_test_id: Mapped[int] = mapped_column(
        ForeignKey("reading_tests.id", ondelete="CASCADE"), index=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finish_reason: Mapped[FinishReasonEnum | None] = mapped_column(finish_reason_enum, nullable=True)

    user: Mapped[User] = relationship()
    reading_test: Mapped[ReadingTest] = relationship()
    question_answers: Mapped[list[ReadingExamQuestionAnswer]] = relationship(
        back_populates="exam", cascade="all, delete-orphan"
    )


class ReadingExamQuestionAnswer(TimestampMixin, Base):
    __tablename__ = "reading_exam_question_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("reading_exams.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("reading_questions.id", ondelete="CASCADE"), index=True
    )
    user_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    exam: Mapped[ReadingExam] = relationship(back_populates="question_answers")
    question: Mapped[ReadingQuestion] = relationship()

    __table_args__ = (
        UniqueConstraint("exam_id", "question_id", name="uq_reading_exam_question_answer"),
    )


class ListeningExam(TimestampMixin, Base):
    __tablename__ = "listening_exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    listening_test_id: Mapped[int] = mapped_column(
        ForeignKey("listening_tests.id", ondelete="CASCADE"), index=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finish_reason: Mapped[FinishReasonEnum | None] = mapped_column(finish_reason_enum, nullable=True)

    user: Mapped[User] = relationship()
    listening_test: Mapped[ListeningTest] = relationship()
    question_answers: Mapped[list[ListeningExamQuestionAnswer]] = relationship(
        back_populates="exam", cascade="all, delete-orphan"
    )


class ListeningExamQuestionAnswer(TimestampMixin, Base):
    __tablename__ = "listening_exam_question_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("listening_exams.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("listening_questions.id", ondelete="CASCADE"), index=True
    )
    user_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    exam: Mapped[ListeningExam] = relationship(back_populates="question_answers")
    question: Mapped[ListeningQuestion] = relationship()

    __table_args__ = (
        UniqueConstraint("exam_id", "question_id", name="uq_listening_exam_question_answer"),
    )


class WritingExam(TimestampMixin, Base):
    __tablename__ = "writing_exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    writing_test_id: Mapped[int] = mapped_column(
        ForeignKey("writing_tests.id", ondelete="CASCADE"), index=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finish_reason: Mapped[FinishReasonEnum | None] = mapped_column(finish_reason_enum, nullable=True)

    user: Mapped[User] = relationship()
    writing_test: Mapped[WritingTest] = relationship()
    writing_parts: Mapped[list[WritingExamPart]] = relationship(
        back_populates="exam", cascade="all, delete-orphan"
    )


class WritingExamPart(TimestampMixin, Base):
    __tablename__ = "writing_exam_parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("writing_exams.id", ondelete="CASCADE"), index=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("writing_parts.id", ondelete="CASCADE"), index=True)
    essay: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    corrections: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), nullable=True)

    exam: Mapped[WritingExam] = relationship(back_populates="writing_parts")
    part: Mapped[WritingPart] = relationship()

    __table_args__ = (
        UniqueConstraint("exam_id", "part_id", name="uq_writing_exam_part"),
    )


class AdminAuditLog(TimestampMixin, Base):
    __tablename__ = "admin_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    admin_user: Mapped[User] = relationship()


Index("ix_reading_passage_test_passage", ReadingPassage.test_id, ReadingPassage.passage_number)
Index("ix_reading_block_passage_order", ReadingQuestionBlock.passage_id, ReadingQuestionBlock.order)
Index("ix_reading_question_block_order", ReadingQuestion.question_block_id, ReadingQuestion.order)
Index("ix_listening_part_test_order", ListeningPart.test_id, ListeningPart.order)
Index("ix_listening_block_part_order", ListeningQuestionBlock.part_id, ListeningQuestionBlock.order)
Index("ix_listening_question_block_order", ListeningQuestion.question_block_id, ListeningQuestion.order)
Index("ix_progress_user_test_date", UserProgress.user_id, UserProgress.test_date)
