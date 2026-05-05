from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.article import ArticleDetail, ArticleListResponse, ArticleStateResponse
from app.services import articles


router = APIRouter(prefix="/api/articles", tags=["Articles"])

AnalysisStatus = Literal["pending", "queued", "processing", "completed", "failed"]
PriorityLevel = Literal["low", "medium", "high", "critical"]


@router.get("", response_model=ArticleListResponse)
def list_articles(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    source_id: Annotated[int | None, Query()] = None,
    analysis_status: Annotated[AnalysisStatus | None, Query()] = None,
    priority_level: Annotated[PriorityLevel | None, Query()] = None,
    q: Annotated[str | None, Query(min_length=1, max_length=200)] = None,
    saved: Annotated[bool | None, Query()] = None,
    archived: Annotated[bool | None, Query()] = None,
) -> ArticleListResponse:
    return articles.list_articles(
        db,
        limit=limit,
        offset=offset,
        source_id=source_id,
        analysis_status=analysis_status,
        priority_level=priority_level,
        q=q,
        saved=saved,
        archived=archived,
    )


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(
    article_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ArticleDetail:
    article = articles.get_article_detail(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    return article


@router.post("/{article_id}/save", response_model=ArticleStateResponse)
def save_article(
    article_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ArticleStateResponse:
    if articles.get_article(db, article_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    return articles.set_saved(db, article_id, True)


@router.post("/{article_id}/archive", response_model=ArticleStateResponse)
def archive_article(
    article_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ArticleStateResponse:
    if articles.get_article(db, article_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    return articles.set_archived(db, article_id, True)

