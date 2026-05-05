from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.rss_source import RssSourceRead


class AnalysisSummary(BaseModel):
    status: str | None = None
    priority_level: str | None = None
    recommended_action: str | None = None
    sentiment: str | None = None
    importance_score: int | None = None


class ReadingStateRead(BaseModel):
    is_read: bool
    is_saved: bool
    is_archived: bool
    read_at: datetime | None


class ArticleListItem(BaseModel):
    id: int
    source_id: int | None
    title: str
    url: str
    author: str | None
    published_at: datetime | None
    summary: str | None
    language: str | None
    analysis_status: str
    created_at: datetime
    analysis: AnalysisSummary | None = None
    reading_state: ReadingStateRead | None = None

    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    items: list[ArticleListItem]
    total: int
    limit: int
    offset: int


class ArticleDetail(ArticleListItem):
    content: str | None
    source: RssSourceRead | None = None
    tags: list[str] = []


class ArticleStateResponse(BaseModel):
    article_id: int
    is_read: bool
    is_saved: bool
    is_archived: bool
    read_at: datetime | None

