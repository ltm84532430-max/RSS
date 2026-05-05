from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rss_source import RssSource
from app.schemas.rss_source import RssSourceCreate, RssSourceUpdate


def list_sources(
    db: Session,
    *,
    enabled: bool | None = None,
    category: str | None = None,
) -> list[RssSource]:
    stmt = select(RssSource)
    if enabled is not None:
        stmt = stmt.where(RssSource.enabled == enabled)
    if category:
        stmt = stmt.where(RssSource.category == category)
    stmt = stmt.order_by(RssSource.name.asc())
    return list(db.scalars(stmt).all())


def get_source(db: Session, source_id: int) -> RssSource | None:
    return db.get(RssSource, source_id)


def create_source(db: Session, payload: RssSourceCreate) -> RssSource:
    source = RssSource(**payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def update_source(db: Session, source: RssSource, payload: RssSourceUpdate) -> RssSource:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(source, key, value)
    db.commit()
    db.refresh(source)
    return source


def delete_source(db: Session, source: RssSource) -> None:
    db.delete(source)
    db.commit()

