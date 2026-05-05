"""create initial AI RSS schema

Revision ID: 20260501_0001
Revises:
Create Date: 2026-05-01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260501_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rss_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("fetch_interval_minutes", sa.Integer(), server_default="60", nullable=False),
        sa.Column("last_fetch_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_index("ix_rss_sources_category", "rss_sources", ["category"])
    op.create_index("ix_rss_sources_enabled", "rss_sources", ["enabled"])

    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("url_hash", sa.String(length=64), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("language", sa.String(length=20), nullable=True),
        sa.Column("analysis_status", sa.String(length=30), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "analysis_status in ('pending', 'queued', 'processing', 'completed', 'failed')",
            name="ck_articles_analysis_status",
        ),
        sa.ForeignKeyConstraint(["source_id"], ["rss_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_index("ix_articles_analysis_status", "articles", ["analysis_status"])
    op.create_index("ix_articles_content_hash", "articles", ["content_hash"])
    op.create_index("ix_articles_published_at", "articles", ["published_at"])
    op.create_index("ix_articles_source_id", "articles", ["source_id"])
    op.create_index("ix_articles_url_hash", "articles", ["url_hash"])

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "article_analysis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("structured_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("cognitive_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("decision_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=30), server_default="queued", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("model_provider", sa.String(length=50), nullable=True),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("task_id", sa.String(length=255), nullable=True),
        sa.Column("priority_level", sa.String(length=30), nullable=True),
        sa.Column("recommended_action", sa.String(length=30), nullable=True),
        sa.Column("sentiment", sa.String(length=30), nullable=True),
        sa.Column("importance_score", sa.Integer(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status in ('queued', 'processing', 'completed', 'failed')",
            name="ck_article_analysis_status",
        ),
        sa.CheckConstraint(
            "priority_level is null or priority_level in ('low', 'medium', 'high', 'critical')",
            name="ck_article_analysis_priority_level",
        ),
        sa.CheckConstraint(
            "recommended_action is null or recommended_action in ('ignore', 'read', 'save', 'track', 'alert')",
            name="ck_article_analysis_recommended_action",
        ),
        sa.CheckConstraint(
            "sentiment is null or sentiment in ('positive', 'neutral', 'negative', 'mixed')",
            name="ck_article_analysis_sentiment",
        ),
        sa.CheckConstraint(
            "importance_score is null or (importance_score >= 1 and importance_score <= 10)",
            name="ck_article_analysis_importance_score",
        ),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("article_id"),
    )
    op.create_index("ix_article_analysis_importance_score", "article_analysis", ["importance_score"])
    op.create_index("ix_article_analysis_priority_level", "article_analysis", ["priority_level"])
    op.create_index("ix_article_analysis_recommended_action", "article_analysis", ["recommended_action"])
    op.create_index("ix_article_analysis_sentiment", "article_analysis", ["sentiment"])
    op.create_index("ix_article_analysis_status", "article_analysis", ["status"])
    op.create_index("ix_article_analysis_task_id", "article_analysis", ["task_id"])

    op.create_table(
        "article_tags",
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id", "tag_id"),
    )
    op.create_index("ix_article_tags_article_id", "article_tags", ["article_id"])
    op.create_index("ix_article_tags_tag_id", "article_tags", ["tag_id"])

    op.create_table(
        "user_reading_state",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_saved", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_archived", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("article_id"),
    )
    op.create_index("ix_user_reading_state_article_id", "user_reading_state", ["article_id"])
    op.create_index("ix_user_reading_state_is_archived", "user_reading_state", ["is_archived"])
    op.create_index("ix_user_reading_state_is_saved", "user_reading_state", ["is_saved"])


def downgrade() -> None:
    op.drop_index("ix_user_reading_state_is_saved", table_name="user_reading_state")
    op.drop_index("ix_user_reading_state_is_archived", table_name="user_reading_state")
    op.drop_index("ix_user_reading_state_article_id", table_name="user_reading_state")
    op.drop_table("user_reading_state")

    op.drop_index("ix_article_tags_tag_id", table_name="article_tags")
    op.drop_index("ix_article_tags_article_id", table_name="article_tags")
    op.drop_table("article_tags")

    op.drop_index("ix_article_analysis_task_id", table_name="article_analysis")
    op.drop_index("ix_article_analysis_status", table_name="article_analysis")
    op.drop_index("ix_article_analysis_sentiment", table_name="article_analysis")
    op.drop_index("ix_article_analysis_recommended_action", table_name="article_analysis")
    op.drop_index("ix_article_analysis_priority_level", table_name="article_analysis")
    op.drop_index("ix_article_analysis_importance_score", table_name="article_analysis")
    op.drop_table("article_analysis")

    op.drop_table("tags")

    op.drop_index("ix_articles_url_hash", table_name="articles")
    op.drop_index("ix_articles_source_id", table_name="articles")
    op.drop_index("ix_articles_published_at", table_name="articles")
    op.drop_index("ix_articles_content_hash", table_name="articles")
    op.drop_index("ix_articles_analysis_status", table_name="articles")
    op.drop_table("articles")

    op.drop_index("ix_rss_sources_enabled", table_name="rss_sources")
    op.drop_index("ix_rss_sources_category", table_name="rss_sources")
    op.drop_table("rss_sources")

