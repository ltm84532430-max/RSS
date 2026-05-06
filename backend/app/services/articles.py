from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.analysis import ArticleAnalysis
from app.models.article import Article
from app.models.reading_state import UserReadingState
from app.models.tag import ArticleTag
from app.schemas.article import (
    AnalysisSummary,
    ArticleDetail,
    ArticleListItem,
    ArticleListResponse,
    ArticleStateResponse,
    ReadingStateRead,
)
from app.schemas.tag import TagRead


def get_article(db: Session, article_id: int) -> Article | None:
    return db.get(Article, article_id)


def _apply_article_filters(
    stmt: Select[tuple[Article]],
    *,
    source_id: int | None,
    analysis_status: str | None,
    priority_level: str | None,
    q: str | None,
    saved: bool | None,
    archived: bool | None,
) -> Select[tuple[Article]]:
    if source_id is not None:
        stmt = stmt.where(Article.source_id == source_id)
    if analysis_status is not None:
        stmt = stmt.where(Article.analysis_status == analysis_status)
    if priority_level is not None:
        stmt = stmt.join(ArticleAnalysis, ArticleAnalysis.article_id == Article.id).where(
            ArticleAnalysis.priority_level == priority_level
        )
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            or_(
                Article.title.ilike(pattern),
                Article.summary.ilike(pattern),
                Article.content.ilike(pattern),
            )
        )
    if saved is not None:
        stmt = stmt.join(UserReadingState, UserReadingState.article_id == Article.id).where(
            UserReadingState.is_saved == saved
        )
    if archived is not None:
        stmt = stmt.join(UserReadingState, UserReadingState.article_id == Article.id).where(
            UserReadingState.is_archived == archived
        )
    return stmt


def list_articles(
    db: Session,
    *,
    limit: int,
    offset: int,
    source_id: int | None,
    analysis_status: str | None,
    priority_level: str | None,
    q: str | None,
    saved: bool | None,
    archived: bool | None,
) -> ArticleListResponse:
    base_stmt = _apply_article_filters(
        select(Article),
        source_id=source_id,
        analysis_status=analysis_status,
        priority_level=priority_level,
        q=q,
        saved=saved,
        archived=archived,
    )

    total_stmt = select(func.count()).select_from(base_stmt.order_by(None).subquery())
    total = db.scalar(total_stmt) or 0

    stmt = (
        base_stmt.options(
            selectinload(Article.analysis),
            selectinload(Article.reading_state),
        )
        .order_by(Article.published_at.desc().nullslast(), Article.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = [_to_list_item(article) for article in db.scalars(stmt).unique().all()]
    return ArticleListResponse(items=items, total=total, limit=limit, offset=offset)


def get_article_detail(db: Session, article_id: int) -> ArticleDetail | None:
    stmt = (
        select(Article)
        .where(Article.id == article_id)
        .options(
            selectinload(Article.source),
            selectinload(Article.analysis),
            selectinload(Article.reading_state),
            selectinload(Article.tags).selectinload(ArticleTag.tag),
        )
    )
    article = db.scalars(stmt).first()
    if article is None:
        return None
    return _to_detail(article)


def set_saved(db: Session, article_id: int, value: bool) -> ArticleStateResponse:
    state = _get_or_create_state(db, article_id)
    state.is_saved = value
    db.commit()
    db.refresh(state)
    return _to_state_response(state)


def set_archived(db: Session, article_id: int, value: bool) -> ArticleStateResponse:
    state = _get_or_create_state(db, article_id)
    state.is_archived = value
    db.commit()
    db.refresh(state)
    return _to_state_response(state)


def _get_or_create_state(db: Session, article_id: int) -> UserReadingState:
    state = db.scalar(
        select(UserReadingState).where(UserReadingState.article_id == article_id)
    )
    if state is None:
        state = UserReadingState(article_id=article_id)
        db.add(state)
        db.flush()
    return state


def _analysis_summary(analysis: ArticleAnalysis | None) -> AnalysisSummary | None:
    if analysis is None:
        return None
    return AnalysisSummary(
        status=analysis.status,
        priority_level=analysis.priority_level,
        recommended_action=analysis.recommended_action,
        sentiment=analysis.sentiment,
        importance_score=analysis.importance_score,
    )


def _reading_state(state: UserReadingState | None) -> ReadingStateRead | None:
    if state is None:
        return None
    return ReadingStateRead(
        is_read=state.is_read,
        is_saved=state.is_saved,
        is_archived=state.is_archived,
        read_at=state.read_at,
    )


def _to_list_item(article: Article) -> ArticleListItem:
    return ArticleListItem(
        id=article.id,
        source_id=article.source_id,
        title=article.title,
        url=article.url,
        author=article.author,
        published_at=article.published_at,
        summary=article.summary,
        language=article.language,
        analysis_status=article.analysis_status,
        created_at=article.created_at,
        analysis=_analysis_summary(article.analysis),
        reading_state=_reading_state(article.reading_state),
    )


def _to_detail(article: Article) -> ArticleDetail:
    base = _to_list_item(article).model_dump()
    return ArticleDetail(
        **base,
        content=article.content,
        source=article.source,
        tags=[
            TagRead.model_validate(article_tag.tag)
            for article_tag in article.tags
            if article_tag.tag
        ],
    )


def _to_state_response(state: UserReadingState) -> ArticleStateResponse:
    return ArticleStateResponse(
        article_id=state.article_id,
        is_read=state.is_read,
        is_saved=state.is_saved,
        is_archived=state.is_archived,
        read_at=state.read_at,
    )
