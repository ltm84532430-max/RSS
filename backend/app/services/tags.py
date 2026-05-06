from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.tag import ArticleTag, Tag
from app.schemas.tag import TagRead
from app.services import articles as article_service


def list_tags(db: Session) -> list[TagRead]:
    stmt = select(Tag).order_by(func.lower(Tag.name))
    return [TagRead.model_validate(tag) for tag in db.scalars(stmt).all()]


def create_tag(db: Session, name: str) -> TagRead:
    normalized = _normalize_tag_name(name)
    existing = _get_tag_by_name(db, normalized)
    if existing is not None:
        return TagRead.model_validate(existing)

    tag = Tag(name=normalized)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return TagRead.model_validate(tag)


def add_tag_to_article(db: Session, article_id: int, name: str):
    normalized = _normalize_tag_name(name)
    article = db.get(Article, article_id)
    if article is None:
        return None

    tag = _get_tag_by_name(db, normalized)
    if tag is None:
        tag = Tag(name=normalized)
        db.add(tag)
        db.flush()

    relation = db.scalar(
        select(ArticleTag).where(
            ArticleTag.article_id == article_id,
            ArticleTag.tag_id == tag.id,
        )
    )
    if relation is None:
        db.add(ArticleTag(article_id=article_id, tag_id=tag.id))

    db.commit()
    return article_service.get_article_detail(db, article_id)


def remove_tag_from_article(db: Session, article_id: int, tag_id: int):
    article = db.get(Article, article_id)
    if article is None:
        return None

    relation = db.scalar(
        select(ArticleTag).where(
            ArticleTag.article_id == article_id,
            ArticleTag.tag_id == tag_id,
        )
    )
    if relation is None:
        return article_service.get_article_detail(db, article_id)

    db.delete(relation)
    db.commit()
    return article_service.get_article_detail(db, article_id)


def _normalize_tag_name(value: str) -> str:
    normalized = " ".join(value.strip().split())
    if not normalized:
        raise ValueError("Tag name cannot be empty.")
    if len(normalized) > 100:
        raise ValueError("Tag name must be 100 characters or fewer.")
    return normalized


def _get_tag_by_name(db: Session, name: str) -> Tag | None:
    return db.scalar(select(Tag).where(func.lower(Tag.name) == name.lower()))
