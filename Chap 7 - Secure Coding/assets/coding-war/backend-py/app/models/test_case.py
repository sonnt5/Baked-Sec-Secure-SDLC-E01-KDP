"""
TestCase Model
Equivalent to: Prisma model TestCase
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
    )
    input_file: Mapped[str] = mapped_column(Text, nullable=False, default="")      # S3 object key (legacy)
    output_file: Mapped[str] = mapped_column(Text, nullable=False, default="")     # S3 object key (legacy)
    input_content: Mapped[str | None] = mapped_column(Text, nullable=True)         # Inline text (admin TXT)
    output_content: Mapped[str | None] = mapped_column(Text, nullable=True)        # Inline text (admin TXT)
    input_checksum: Mapped[str] = mapped_column(String, nullable=False, default="")
    output_checksum: Mapped[str] = mapped_column(String, nullable=False, default="")
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    problem = relationship("Problem", back_populates="test_cases")
    test_case_results = relationship("TestCaseResult", back_populates="test_case", lazy="selectin")

    __table_args__ = (
        Index("ix_test_cases_problem_id", "problem_id"),
        Index("ix_test_cases_problem_order", "problem_id", "order_index"),
    )
