"""
Submission & TestCaseResult Models
Equivalent to: Prisma models Submission, TestCaseResult
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import Language, SubmissionStatus


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False
    )
    contest_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contests.id"), nullable=True
    )
    language: Mapped[Language] = mapped_column(
        ENUM(Language, name="language", create_type=False), nullable=False
    )
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        ENUM(SubmissionStatus, name="submission_status", create_type=False),
        default=SubmissionStatus.QUEUED,
        nullable=False,
    )
    verdict: Mapped[str | None] = mapped_column(String(50))
    execution_time: Mapped[int | None] = mapped_column(Integer)  # milliseconds
    memory_used: Mapped[int | None] = mapped_column(Integer)  # MB
    compilation_error: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    judged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    contest_relative_time: Mapped[int | None] = mapped_column(Integer)  # minutes from contest start

    # Relationships
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    contest = relationship("Contest", back_populates="submissions")
    test_case_results = relationship(
        "TestCaseResult",
        back_populates="submission",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_submissions_user_id", "user_id"),
        Index("ix_submissions_problem_id", "problem_id"),
        Index("ix_submissions_contest_id", "contest_id"),
        Index("ix_submissions_status", "status"),
        Index("ix_submissions_submitted_at", "submitted_at"),
    )


class TestCaseResult(Base):
    __tablename__ = "test_case_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("test_cases.id"), nullable=False
    )
    status: Mapped[SubmissionStatus] = mapped_column(
        ENUM(SubmissionStatus, name="submission_status", create_type=False),
        nullable=False,
    )
    execution_time: Mapped[int | None] = mapped_column(Integer)  # milliseconds
    memory_used: Mapped[int | None] = mapped_column(Integer)  # MB
    output: Mapped[str | None] = mapped_column(Text)

    # Relationships
    submission = relationship("Submission", back_populates="test_case_results")
    test_case = relationship("TestCase", back_populates="test_case_results")

    __table_args__ = (
        Index("ix_test_case_results_submission_id", "submission_id"),
        Index("ix_test_case_results_test_case_id", "test_case_id"),
    )
