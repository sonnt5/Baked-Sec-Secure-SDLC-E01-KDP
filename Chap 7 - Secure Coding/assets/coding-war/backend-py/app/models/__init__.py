"""
SQLAlchemy Models — All 8 models from Prisma schema
Equivalent to: backend/prisma/schema.prisma
"""

from app.models.user import User
from app.models.problem import Problem
from app.models.test_case import TestCase
from app.models.submission import Submission, TestCaseResult
from app.models.contest import Contest, ContestProblem, ContestParticipant
from app.models.enums import (
    Role,
    Difficulty,
    Visibility,
    Language,
    SubmissionStatus,
    ScoringRule,
)

__all__ = [
    "User",
    "Problem",
    "TestCase",
    "Submission",
    "TestCaseResult",
    "Contest",
    "ContestProblem",
    "ContestParticipant",
    "Role",
    "Difficulty",
    "Visibility",
    "Language",
    "SubmissionStatus",
    "ScoringRule",
]
