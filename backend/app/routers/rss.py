from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.rss_source import (
    RssSourceCreate,
    RssSourceFetchResponse,
    RssSourceRead,
    RssSourceUpdate,
)
from app.services import rss_fetcher
from app.services import rss_sources


router = APIRouter(prefix="/api/rss-sources", tags=["RSS Sources"])


@router.get("", response_model=list[RssSourceRead])
def list_rss_sources(
    db: Annotated[Session, Depends(get_db)],
    enabled: Annotated[bool | None, Query()] = None,
    category: Annotated[str | None, Query(max_length=100)] = None,
) -> list[RssSourceRead]:
    return rss_sources.list_sources(db, enabled=enabled, category=category)


@router.post("", response_model=RssSourceRead, status_code=status.HTTP_201_CREATED)
def create_rss_source(
    payload: RssSourceCreate,
    db: Annotated[Session, Depends(get_db)],
) -> RssSourceRead:
    try:
        return rss_sources.create_source(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="RSS source URL already exists.",
        ) from exc


@router.get("/{source_id}", response_model=RssSourceRead)
def get_rss_source(
    source_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> RssSourceRead:
    source = rss_sources.get_source(db, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSS source not found.")
    return source


@router.put("/{source_id}", response_model=RssSourceRead)
def update_rss_source(
    source_id: int,
    payload: RssSourceUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> RssSourceRead:
    source = rss_sources.get_source(db, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSS source not found.")

    try:
        return rss_sources.update_source(db, source, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="RSS source URL already exists.",
        ) from exc


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rss_source(
    source_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    source = rss_sources.get_source(db, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSS source not found.")
    rss_sources.delete_source(db, source)


@router.post(
    "/{source_id}/fetch",
    response_model=RssSourceFetchResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def fetch_rss_source(
    source_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> RssSourceFetchResponse:
    source = rss_sources.get_source(db, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RSS source not found.")

    return RssSourceFetchResponse.model_validate(
        rss_fetcher.fetch_source(db, source),
        from_attributes=True,
    )
