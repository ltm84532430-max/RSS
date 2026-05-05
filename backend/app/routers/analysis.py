from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analysis import AnalysisRead, AnalysisStatusRead, ReanalyzeResponse
from app.services import analysis as analysis_service
from app.services import articles as articles_service


router = APIRouter(prefix="/api/articles", tags=["Analysis"])


@router.get("/{article_id}/analysis", response_model=AnalysisRead)
def get_article_analysis(
    article_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> AnalysisRead:
    article = articles_service.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    return analysis_service.get_analysis(db, article)


@router.get("/{article_id}/analysis/status", response_model=AnalysisStatusRead)
def get_article_analysis_status(
    article_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> AnalysisStatusRead:
    article = articles_service.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    return analysis_service.get_analysis_status(db, article)


@router.post(
    "/{article_id}/reanalyze",
    response_model=ReanalyzeResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def reanalyze_article(
    article_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ReanalyzeResponse:
    article = articles_service.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    return analysis_service.enqueue_reanalysis(db, article)

