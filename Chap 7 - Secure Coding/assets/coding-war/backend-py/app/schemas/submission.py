"""
Submission Pydantic Schemas
Equivalent to: Zod schemas in backend/src/utils/schemas.ts (submission section)
"""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateSubmissionRequest(BaseModel):
    problem_id: str = Field(..., alias="problemId")
    language: str = Field(..., pattern=r"^(C|CPP|PYTHON|JAVA)$")
    source_code: str = Field(..., min_length=1, max_length=65536, alias="sourceCode")
    contest_id: str | None = Field(None, alias="contestId")

    model_config = {"populate_by_name": True}


class SubmissionResponse(BaseModel):
    id: str
    problem_id: str
    problem_title: str | None = None
    user_id: str
    username: str | None = None
    language: str
    source_code: str | None = None
    status: str
    verdict: str | None = None
    execution_time: int | None = None
    memory_used: int | None = None
    compilation_error: str | None = None
    test_case_results: list[dict] | None = None
    submitted_at: str
    judged_at: str | None = None


class SubmissionListResponse(BaseModel):
    submissions: list[SubmissionResponse]
    total: int
    page: int
    total_pages: int
