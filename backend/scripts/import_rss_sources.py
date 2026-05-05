from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from sqlalchemy import select

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal  # noqa: E402
from app.models.rss_source import RssSource  # noqa: E402


@dataclass(frozen=True)
class OpmlSource:
    name: str
    url: str
    category: str | None


def parse_opml(path: Path) -> list[OpmlSource]:
    root = ET.parse(path).getroot()
    body = root.find("body")
    if body is None:
        return []

    sources: list[OpmlSource] = []

    def walk(node: ET.Element, category: str | None = None) -> None:
        node_title = node.attrib.get("title") or node.attrib.get("text")
        xml_url = node.attrib.get("xmlUrl")
        if xml_url:
            sources.append(
                OpmlSource(
                    name=node_title or xml_url,
                    url=xml_url,
                    category=category,
                )
            )
            return

        next_category = node_title or category
        for child in node.findall("outline"):
            walk(child, next_category)

    for outline in body.findall("outline"):
        walk(outline)
    return sources


def import_sources(path: Path, *, update_existing: bool) -> tuple[int, int, int]:
    sources = parse_opml(path)
    created = 0
    updated = 0
    skipped = 0

    with SessionLocal() as db:
        for source in sources:
            existing = db.scalar(select(RssSource).where(RssSource.url == source.url))
            if existing is None:
                db.add(
                    RssSource(
                        name=source.name,
                        url=source.url,
                        category=source.category,
                        enabled=True,
                    )
                )
                created += 1
                continue

            if update_existing:
                existing.name = source.name
                existing.category = source.category
                existing.enabled = True
                updated += 1
            else:
                skipped += 1

        db.commit()

    return len(sources), created, updated + skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Import RSS sources from an OPML file.")
    parser.add_argument("path", type=Path, help="Path to .opml file")
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Update name/category/enabled for sources whose URL already exists.",
    )
    args = parser.parse_args()

    total, created, existing = import_sources(args.path, update_existing=args.update_existing)
    print(f"parsed={total} created={created} existing={existing}")


if __name__ == "__main__":
    main()

