from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserReadingState(Base):
    __tablename__ = "user_reading_state"
    __table_args__ = (
        Index("ix_user_reading_state_article_id", "article_id"),
        Index("ix_user_reading_state_is_saved", "is_saved"),
        Index("ix_user_reading_state_is_archived", "is_archived"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_saved: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    article = relationship("Article", back_populates="reading_state")

