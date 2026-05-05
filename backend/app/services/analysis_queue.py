from datetime import UTC, datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.ai.pipeline import run_ai_pipeline
from app.ai.providers import current_model_name, current_provider_name
from app.models.analysis import ArticleAnalysis
from app.models.article import Article


def claim_next_queued_analysis(db: Session) -> ArticleAnalysis | None:
    stmt: Select[tuple[int]] = (
        select(ArticleAnalysis.id)
        .where(ArticleAnalysis.status == "queued")
        .order_by(ArticleAnalysis.updated_at.asc(), ArticleAnalysis.id.asc())
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    analysis_id = db.scalar(stmt)
    if analysis_id is None:
        return None

    analysis = db.scalar(
        select(ArticleAnalysis)
        .where(ArticleAnalysis.id == analysis_id)
        .options(joinedload(ArticleAnalysis.article))
    )
    if analysis is None:
        return None

    now = datetime.now(UTC)
    analysis.status = "processing"
    analysis.error_message = None
    analysis.updated_at = now
    if analysis.article is not None:
        analysis.article.analysis_status = "processing"
    db.commit()
    db.refresh(analysis)
    return analysis


def process_analysis_by_id(db: Session, analysis_id: int) -> ArticleAnalysis:
    analysis = db.scalar(
        select(ArticleAnalysis)
        .where(ArticleAnalysis.id == analysis_id)
        .options(joinedload(ArticleAnalysis.article))
    )
    if analysis is None or analysis.article is None:
        raise ValueError(f"Analysis row {analysis_id} does not exist or is missing article.")

    article = analysis.article
    result = run_ai_pipeline(article)
    now = datetime.now(UTC)

    structured = result.structured_result
    decision = result.decision_result
    recommended_action = _normalize_recommended_action(decision.get("recommended_action"))

    analysis.structured_result = structured
    analysis.cognitive_result = result.cognitive_result
    analysis.decision_result = decision
    analysis.status = "completed"
    analysis.error_message = None
    analysis.model_provider = current_provider_name()
    analysis.model_name = current_model_name()
    analysis.priority_level = decision.get("priority_level")
    analysis.recommended_action = recommended_action
    analysis.sentiment = structured.get("sentiment")
    analysis.importance_score = structured.get("importance_score")
    analysis.analyzed_at = now
    analysis.updated_at = now
    article.analysis_status = "completed"
    db.commit()
    db.refresh(analysis)
    return analysis


def mark_analysis_failed(db: Session, analysis_id: int, message: str) -> None:
    analysis = db.scalar(
        select(ArticleAnalysis)
        .where(ArticleAnalysis.id == analysis_id)
        .options(joinedload(ArticleAnalysis.article))
    )
    if analysis is None:
        return
    now = datetime.now(UTC)
    analysis.status = "failed"
    analysis.error_message = message
    analysis.updated_at = now
    if analysis.article is not None:
        analysis.article.analysis_status = "failed"
    db.commit()


def _normalize_recommended_action(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None

    if normalized in {"alert", "track", "read", "ignore", "save"}:
        return normalized

    if any(token in normalized for token in ("urgent", "immediate", "alert", "hedg")):
        return "alert"
    if any(token in normalized for token in ("track", "monitor", "watch", "follow")):
        return "track"
    if any(token in normalized for token in ("save", "bookmark", "keep")):
        return "save"
    if any(token in normalized for token in ("ignore", "skip", "low priority", "no action")):
        return "ignore"
    if any(token in normalized for token in ("read", "review", "analyze", "assess")):
        return "read"
    return "read"
