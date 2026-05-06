from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.tag import TagCreate, TagRead
from app.services import tags as tags_service


router = APIRouter(prefix="/api/tags", tags=["Tags"])


@router.get("", response_model=list[TagRead])
def list_tags(db: Annotated[Session, Depends(get_db)]) -> list[TagRead]:
    return tags_service.list_tags(db)


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
    payload: TagCreate,
    db: Annotated[Session, Depends(get_db)],
) -> TagRead:
    try:
        return tags_service.create_tag(db, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
