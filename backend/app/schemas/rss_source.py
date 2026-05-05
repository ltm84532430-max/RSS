from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RssSourceBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    url: str = Field(min_length=1)
    category: str | None = Field(default=None, max_length=100)
    enabled: bool = True
    fetch_interval_minutes: int = Field(default=60, ge=1)


class RssSourceCreate(RssSourceBase):
    pass


class RssSourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    url: str | None = Field(default=None, min_length=1)
    category: str | None = Field(default=None, max_length=100)
    enabled: bool | None = None
    fetch_interval_minutes: int | None = Field(default=None, ge=1)


class RssSourceRead(RssSourceBase):
    id: int
    last_fetch_time: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RssSourceFetchResponse(BaseModel):
    source_id: int
    fetched_count: int
    inserted_count: int
    queued_analysis_count: int
    status: str
    message: str

