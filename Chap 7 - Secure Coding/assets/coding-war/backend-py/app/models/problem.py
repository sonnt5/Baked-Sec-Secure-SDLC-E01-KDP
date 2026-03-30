"""
Problem Model
Equivalent to: Prisma model Problem
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, Index, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import Difficulty, Visibility


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(
        ENUM(Difficulty, name="difficulty", create_type=False), nullable=False
    )
    time_limit: Mapped[int] = mapped_column(Integer, nullable=False)  # milliseconds
    memory_limit: Mapped[int] = mapped_column(Integer, nullable=False)  # MB
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
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
    test_cases = relationship("TestCase", back_populates="problem", lazy="selectin", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="problem", lazy="selectin")
    contest_problems = relationship("ContestProblem", back_populates="problem", lazy="selectin")

    __table_args__ = (
        Index("ix_problems_difficulty", "difficulty"),
        Index("ix_problems_visibility", "visibility"),
        Index("ix_problems_slug", "slug"),
    )
