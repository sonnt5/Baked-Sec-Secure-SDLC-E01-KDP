"""
Contest, ContestProblem, ContestParticipant Models
Equivalent to: Prisma models Contest, ContestProblem, ContestParticipant
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ScoringRule, Visibility


class Contest(Base):
    __tablename__ = "contests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    freeze_time: Mapped[int | None] = mapped_column(Integer)  # Minutes before end
    scoring_rule: Mapped[ScoringRule] = mapped_column(
        ENUM(ScoringRule, name="scoring_rule", create_type=False), nullable=False
    )
    visibility: Mapped[Visibility] = mapped_column(
        ENUM(Visibility, name="visibility", create_type=False),
        default=Visibility.PUBLIC,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    problems = relationship(
        "ContestProblem", back_populates="contest", lazy="selectin", cascade="all, delete-orphan"
    )
    participants = relationship(
        "ContestParticipant", back_populates="contest", lazy="selectin", cascade="all, delete-orphan"
    )
    submissions = relationship("Submission", back_populates="contest", lazy="selectin")

    __table_args__ = (
        Index("ix_contests_start_time", "start_time"),
        Index("ix_contests_end_time", "end_time"),
        Index("ix_contests_slug", "slug"),
    )


class ContestProblem(Base):
    __tablename__ = "contest_problems"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    contest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contests.id", ondelete="CASCADE"),
        nullable=False,
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int | None] = mapped_column(Integer)  # For IOI scoring

    # Relationships
    contest = relationship("Contest", back_populates="problems")
    problem = relationship("Problem", back_populates="contest_problems", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("contest_id", "problem_id", name="uq_contest_problem"),
        Index("ix_contest_problems_contest_id", "contest_id"),
        Index("ix_contest_problems_problem_id", "problem_id"),
    )


class ContestParticipant(Base):
    __tablename__ = "contest_participants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    contest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contests.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    contest = relationship("Contest", back_populates="participants")
    user = relationship("User", back_populates="contest_participations")

    __table_args__ = (
        UniqueConstraint("contest_id", "user_id", name="uq_contest_participant"),
        Index("ix_contest_participants_contest_id", "contest_id"),
        Index("ix_contest_participants_user_id", "user_id"),
    )
