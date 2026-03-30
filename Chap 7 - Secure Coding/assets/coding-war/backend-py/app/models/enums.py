"""
Database Enums
Equivalent to: Prisma schema enums (Role, Difficulty, Visibility, Language, SubmissionStatus, ScoringRule)
"""

import enum


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"


class Difficulty(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class Visibility(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    CONTEST_ONLY = "CONTEST_ONLY"


class Language(str, enum.Enum):
    C = "C"
    CPP = "CPP"
    PYTHON = "PYTHON"
    JAVA = "JAVA"


class SubmissionStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    COMPILING = "COMPILING"
    RUNNING = "RUNNING"
    ACCEPTED = "ACCEPTED"
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    COMPILATION_ERROR = "COMPILATION_ERROR"


class ScoringRule(str, enum.Enum):
    IOI = "IOI"
    ACM = "ACM"
