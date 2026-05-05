from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html import unescape
import re

import feedparser
from sqlalchemy.orm import Session

from app.models.analysis import ArticleAnalysis
from app.models.article import Article
from app.models.rss_source import RssSource
from app.services.analysis_dispatcher import enqueue_article_analysis
from app.services.content_extractor import extract_article_content
from app.services.deduplication import article_exists, content_hash, url_hash


@dataclass(frozen=True)
class FetchResult:
    source_id: int
    fetched_count: int
    inserted_count: int
    queued_analysis_count: int
    status: str
    message: str


def fetch_source(db: Session, source: RssSource) -> FetchResult:
    feed = feedparser.parse(source.url)
    entries = list(feed.entries or [])

    if feed.bozo and not entries:
        return FetchResult(
            source_id=source.id,
            fetched_count=0,
            inserted_count=0,
            queued_analysis_count=0,
            status="failed",
            message=f"Failed to parse RSS feed: {feed.bozo_exception}",
        )

    inserted_count = 0
    queued_analysis_count = 0

    for entry in entries:
        link = _entry_link(entry)
        title = _clean_text(_entry_value(entry, "title")) or "(untitled)"
        if not link:
            continue

        summary = _clean_text(_entry_value(entry, "summary") or _entry_value(entry, "description"))
        content = _extract_content(link, summary)
        article_url_hash = url_hash(link)
        article_content_hash = content_hash(content or summary or title)

        if article_exists(
            db,
            url=link,
            url_hash_value=article_url_hash,
            content_hash_value=article_content_hash,
        ):
            continue

        article = Article(
            source_id=source.id,
            title=title,
            url=link,
            author=_clean_text(_entry_value(entry, "author")),
            published_at=_published_at(entry),
            summary=summary,
            content=content,
            url_hash=article_url_hash,
            content_hash=article_content_hash,
            language=_entry_value(feed.feed, "language"),
            analysis_status="queued",
        )
        db.add(article)
        db.flush()

        task_id = enqueue_article_analysis(article.id)
        db.add(
            ArticleAnalysis(
                article_id=article.id,
                status="queued",
                task_id=task_id,
            )
        )
        inserted_count += 1
        queued_analysis_count += 1

    source.last_fetch_time = datetime.now(UTC)
    db.commit()

    return FetchResult(
        source_id=source.id,
        fetched_count=len(entries),
        inserted_count=inserted_count,
        queued_analysis_count=queued_analysis_count,
        status="ok",
        message="RSS feed fetched and new articles queued for analysis.",
    )


def _entry_link(entry: object) -> str | None:
    link = _entry_value(entry, "link")
    return link.strip() if link else None


def _entry_value(entry: object, key: str) -> str | None:
    if isinstance(entry, dict):
        value = entry.get(key)
    else:
        value = getattr(entry, key, None)
    if value is None:
        return None
    return str(value)


def _clean_text(value: str | None) -> str | None:
    if not value:
        return None
    without_tags = re.sub(r"<[^>]+>", " ", value)
    normalized = " ".join(unescape(without_tags).split())
    return normalized or None


def _extract_content(url: str, fallback: str | None) -> str | None:
    try:
        return extract_article_content(url) or fallback
    except Exception:
        return fallback


def _published_at(entry: object) -> datetime | None:
    value = _entry_value(entry, "published") or _entry_value(entry, "updated")
    if value:
        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=UTC)
            return parsed
        except (TypeError, ValueError):
            pass

    parsed_struct = None
    if isinstance(entry, dict):
        parsed_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    else:
        parsed_struct = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if parsed_struct:
        return datetime(*parsed_struct[:6], tzinfo=UTC)
    return None
