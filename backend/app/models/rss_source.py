from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RssSource(Base):
    __tablename__ = "rss_sources"
    __table_args__ = (
        Index("ix_rss_sources_enabled", "enabled"),
        Index("ix_rss_sources_category", "category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    category: Mapped[str | None] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    fetch_interval_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="60",
    )
    last_fetch_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    articles = relationship(
        "Article",
        back_populates="source",
        passive_deletes=True,
    )
