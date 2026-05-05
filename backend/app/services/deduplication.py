from hashlib import sha256

from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from app.models.article import Article


def content_hash(value: str | None) -> str | None:
    if not value:
        return None
    normalized = " ".join(value.split())
    if not normalized:
        return None
    return sha256(normalized.encode("utf-8")).hexdigest()


def url_hash(url: str) -> str:
    return sha256(url.strip().lower().encode("utf-8")).hexdigest()


def article_exists(db: Session, *, url: str, url_hash_value: str, content_hash_value: str | None) -> bool:
    conditions = [Article.url == url, Article.url_hash == url_hash_value]
    if content_hash_value:
        conditions.append(Article.content_hash == content_hash_value)
    stmt = select(exists().where(or_(*conditions)))
    return bool(db.scalar(stmt))

