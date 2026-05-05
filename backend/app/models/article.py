from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        CheckConstraint(
            "analysis_status in ('pending', 'queued', 'processing', 'completed', 'failed')",
            name="ck_articles_analysis_status",
        ),
        Index("ix_articles_source_id", "source_id"),
        Index("ix_articles_published_at", "published_at"),
        Index("ix_articles_analysis_status", "analysis_status"),
        Index("ix_articles_url_hash", "url_hash"),
        Index("ix_articles_content_hash", "content_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("rss_sources.id", ondelete="SET NULL"),
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    author: Mapped[str | None] = mapped_column(String(255))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    url_hash: Mapped[str | None] = mapped_column(String(64))
    content_hash: Mapped[str | None] = mapped_column(String(64))
    language: Mapped[str | None] = mapped_column(String(20))
    analysis_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    source = relationship("RssSource", back_populates="articles")
    analysis = relationship(
        "ArticleAnalysis",
        back_populates="article",
        cascade="all, delete-orphan",
        uselist=False,
    )
    reading_state = relationship(
        "UserReadingState",
        back_populates="article",
        cascade="all, delete-orphan",
        uselist=False,
    )
    tags = relationship(
        "ArticleTag",
        back_populates="article",
        cascade="all, delete-orphan",
    )

