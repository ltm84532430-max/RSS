from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AnalysisRead(BaseModel):
    article_id: int
    status: str
    structured_result: dict[str, Any] | None
    cognitive_result: dict[str, Any] | None
    decision_result: dict[str, Any] | None
    error_message: str | None
    model_provider: str | None
    model_name: str | None
    task_id: str | None
    priority_level: str | None
    recommended_action: str | None
    sentiment: str | None
    importance_score: int | None
    analyzed_at: datetime | None
    updated_at: datetime | None


class AnalysisStatusRead(BaseModel):
    article_id: int
    status: str
    task_id: str | None
    error_message: str | None
    updated_at: datetime | None


class ReanalyzeResponse(BaseModel):
    article_id: int
    task_id: str
    status: str

