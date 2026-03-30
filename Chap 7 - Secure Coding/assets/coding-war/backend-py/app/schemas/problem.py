"""
Problem Pydantic Schemas
Equivalent to: Zod schemas in backend/src/utils/schemas.ts (problem section)
"""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateProblemRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    difficulty: str = Field(..., pattern=r"^(EASY|MEDIUM|HARD)$")
    time_limit: int = Field(..., ge=100, le=30000, alias="timeLimit")
    memory_limit: int = Field(..., ge=16, le=1024, alias="memoryLimit")
    tags: list[str] = Field(default_factory=list)
    visibility: str = Field(default="PUBLIC", pattern=r"^(PUBLIC|PRIVATE|CONTEST_ONLY)$")

    model_config = {"populate_by_name": True}


class UpdateProblemRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    difficulty: str | None = Field(None, pattern=r"^(EASY|MEDIUM|HARD)$")
    time_limit: int | None = Field(None, ge=100, le=30000, alias="timeLimit")
    memory_limit: int | None = Field(None, ge=16, le=1024, alias="memoryLimit")
    tags: list[str] | None = None
    visibility: str | None = Field(None, pattern=r"^(PUBLIC|PRIVATE|CONTEST_ONLY)$")

    model_config = {"populate_by_name": True}


class ProblemResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    difficulty: str
    time_limit: int
    memory_limit: int
    tags: list[str]
    visibility: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProblemListResponse(BaseModel):
    problems: list[ProblemResponse]
    total: int
    page: int
    total_pages: int
