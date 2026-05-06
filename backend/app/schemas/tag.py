from pydantic import BaseModel, ConfigDict, Field


class TagRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class ArticleTagsResponse(BaseModel):
    article_id: int
    tags: list[TagRead] = Field(default_factory=list)
