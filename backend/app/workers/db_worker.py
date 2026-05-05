from __future__ import annotations

import argparse
import time
import traceback

from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal
from app.models.analysis import ArticleAnalysis
from app.services.analysis_queue import (
    claim_next_queued_analysis,
    mark_analysis_failed,
    process_analysis_by_id,
)


def run_once() -> int:
    processed = 0
    with SessionLocal() as db:
        analysis = claim_next_queued_analysis(db)
        if analysis is None:
            return 0
        analysis_id = analysis.id

    try:
        with SessionLocal() as db:
            process_analysis_by_id(db, analysis_id)
        processed = 1
    except Exception:
        error_message = traceback.format_exc()
        with SessionLocal() as db:
            mark_analysis_failed(db, analysis_id, error_message)
        print(error_message)
        return 0
    return processed


def run_forever() -> None:
    settings = get_settings()
    while True:
        processed = 0
        for _ in range(settings.db_worker_batch_size):
            try:
                result = run_once()
            except Exception as exc:
                print(f"[db_worker] task failed: {exc}")
                result = 0
            processed += result
            if result == 0:
                break
        if processed == 0:
            time.sleep(settings.db_worker_poll_interval_seconds)


def run_analysis_id(analysis_id: int) -> int:
    try:
        with SessionLocal() as db:
            process_analysis_by_id(db, analysis_id)
        return 1
    except Exception:
        error_message = traceback.format_exc()
        with SessionLocal() as db:
            mark_analysis_failed(db, analysis_id, error_message)
        print(error_message)
        return 0


def lookup_analysis_id_by_article_id(article_id: int) -> int | None:
    with SessionLocal() as db:
        return db.scalar(
            select(ArticleAnalysis.id).where(ArticleAnalysis.article_id == article_id)
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Process queued article_analysis rows from PostgreSQL.")
    parser.add_argument("--once", action="store_true", help="Process at most one queued analysis and exit.")
    parser.add_argument("--analysis-id", type=int, help="Process a specific article_analysis row.")
    parser.add_argument("--article-id", type=int, help="Process the analysis row for a specific article.")
    args = parser.parse_args()
    if args.analysis_id is not None:
        processed = run_analysis_id(args.analysis_id)
        print(f"processed={processed}")
        return
    if args.article_id is not None:
        analysis_id = lookup_analysis_id_by_article_id(args.article_id)
        if analysis_id is None:
            print("processed=0")
            return
        processed = run_analysis_id(analysis_id)
        print(f"processed={processed}")
        return
    if args.once:
        processed = run_once()
        print(f"processed={processed}")
        return
    run_forever()


if __name__ == "__main__":
    main()
