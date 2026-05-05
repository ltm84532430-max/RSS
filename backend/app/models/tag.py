from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    articles = relationship(
        "ArticleTag",
        back_populates="tag",
        cascade="all, delete-orphan",
    )


class ArticleTag(Base):
    __tablename__ = "article_tags"
    __table_args__ = (
        Index("ix_article_tags_article_id", "article_id"),
        Index("ix_article_tags_tag_id", "tag_id"),
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )

    article = relationship("Article", back_populates="tags")
    tag = relationship("Tag", back_populates="articles")

