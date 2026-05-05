from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis import ArticleAnalysis
from app.models.article import Article
from app.schemas.analysis import AnalysisRead, AnalysisStatusRead, ReanalyzeResponse
from app.services.analysis_dispatcher import enqueue_article_analysis


def get_analysis(db: Session, article: Article) -> AnalysisRead:
    analysis = _get_analysis_row(db, article.id)
    if analysis is None:
        return AnalysisRead(
            article_id=article.id,
            status=article.analysis_status,
            structured_result=None,
            cognitive_result=None,
            decision_result=None,
            error_message=None,
            model_provider=None,
            model_name=None,
            task_id=None,
            priority_level=None,
            recommended_action=None,
            sentiment=None,
            importance_score=None,
            analyzed_at=None,
            updated_at=None,
        )
    return _to_analysis_read(analysis)


def get_analysis_status(db: Session, article: Article) -> AnalysisStatusRead:
    analysis = _get_analysis_row(db, article.id)
    if analysis is None:
        return AnalysisStatusRead(
            article_id=article.id,
            status=article.analysis_status,
            task_id=None,
            error_message=None,
            updated_at=None,
        )
    return AnalysisStatusRead(
        article_id=article.id,
        status=analysis.status,
        task_id=analysis.task_id,
        error_message=analysis.error_message,
        updated_at=analysis.updated_at,
    )


def enqueue_reanalysis(db: Session, article: Article) -> ReanalyzeResponse:
    task_id = enqueue_article_analysis(article.id)
    now = datetime.now(UTC)
    analysis = _get_analysis_row(db, article.id)
    if analysis is None:
        analysis = ArticleAnalysis(article_id=article.id)
        db.add(analysis)

    analysis.status = "queued"
    analysis.task_id = task_id
    analysis.error_message = None
    analysis.updated_at = now
    article.analysis_status = "queued"

    db.commit()
    return ReanalyzeResponse(article_id=article.id, task_id=task_id, status="queued")


def _get_analysis_row(db: Session, article_id: int) -> ArticleAnalysis | None:
    return db.scalar(select(ArticleAnalysis).where(ArticleAnalysis.article_id == article_id))


def _to_analysis_read(analysis: ArticleAnalysis) -> AnalysisRead:
    return AnalysisRead(
        article_id=analysis.article_id,
        status=analysis.status,
        structured_result=analysis.structured_result,
        cognitive_result=analysis.cognitive_result,
        decision_result=analysis.decision_result,
        error_message=analysis.error_message,
        model_provider=analysis.model_provider,
        model_name=analysis.model_name,
        task_id=analysis.task_id,
        priority_level=analysis.priority_level,
        recommended_action=analysis.recommended_action,
        sentiment=analysis.sentiment,
        importance_score=analysis.importance_score,
        analyzed_at=analysis.analyzed_at,
        updated_at=analysis.updated_at,
    )
