"""
Contest Pydantic Schemas
Equivalent to: Zod schemas in backend/src/utils/schemas.ts (contest section)
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ProblemEntry(BaseModel):
    problem_id: str = Field(..., alias="problemId")
    order_index: int = Field(0, alias="orderIndex")
    points: int | None = Field(None)
    model_config = {"populate_by_name": True}


class CreateContestRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    freeze_time: int | None = Field(None, ge=0, alias="freezeTime")
    scoring_rule: str = Field(..., pattern=r"^(IOI|ACM)$", alias="scoringRule")
    visibility: str = Field(default="PUBLIC", pattern=r"^(PUBLIC|PRIVATE|CONTEST_ONLY)$")
    problems: list[ProblemEntry] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class UpdateContestRequest(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    start_time: datetime | None = Field(None, alias="startTime")
    end_time: datetime | None = Field(None, alias="endTime")
    freeze_time: int | None = Field(None, alias="freezeTime")
    scoring_rule: str | None = Field(None, pattern=r"^(IOI|ACM)$", alias="scoringRule")
    visibility: str | None = None

    model_config = {"populate_by_name": True}


class ContestResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    start_time: datetime
    end_time: datetime
    freeze_time: int | None
    scoring_rule: str
    visibility: str
    participant_count: int = 0
    created_at: datetime
    updated_at: datetime


class ContestListResponse(BaseModel):
    contests: list[ContestResponse]
    total: int
    page: int
    total_pages: int
