from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ArticleAnalysis(Base):
    __tablename__ = "article_analysis"
    __table_args__ = (
        CheckConstraint(
            "status in ('queued', 'processing', 'completed', 'failed')",
            name="ck_article_analysis_status",
        ),
        CheckConstraint(
            "priority_level is null or priority_level in ('low', 'medium', 'high', 'critical')",
            name="ck_article_analysis_priority_level",
        ),
        CheckConstraint(
            "recommended_action is null or recommended_action in ('ignore', 'read', 'save', 'track', 'alert')",
            name="ck_article_analysis_recommended_action",
        ),
        CheckConstraint(
            "sentiment is null or sentiment in ('positive', 'neutral', 'negative', 'mixed')",
            name="ck_article_analysis_sentiment",
        ),
        CheckConstraint(
            "importance_score is null or (importance_score >= 1 and importance_score <= 10)",
            name="ck_article_analysis_importance_score",
        ),
        Index("ix_article_analysis_status", "status"),
        Index("ix_article_analysis_task_id", "task_id"),
        Index("ix_article_analysis_priority_level", "priority_level"),
        Index("ix_article_analysis_recommended_action", "recommended_action"),
        Index("ix_article_analysis_sentiment", "sentiment"),
        Index("ix_article_analysis_importance_score", "importance_score"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    structured_result: Mapped[dict | None] = mapped_column(JSONB)
    cognitive_result: Mapped[dict | None] = mapped_column(JSONB)
    decision_result: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default="queued")
    error_message: Mapped[str | None] = mapped_column(Text)
    model_provider: Mapped[str | None] = mapped_column(String(50))
    model_name: Mapped[str | None] = mapped_column(String(100))
    task_id: Mapped[str | None] = mapped_column(String(255))
    priority_level: Mapped[str | None] = mapped_column(String(30))
    recommended_action: Mapped[str | None] = mapped_column(String(30))
    sentiment: Mapped[str | None] = mapped_column(String(30))
    importance_score: Mapped[int | None] = mapped_column(Integer)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    article = relationship("Article", back_populates="analysis")

