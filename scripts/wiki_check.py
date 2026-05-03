#!/usr/bin/env python3
"""Small maintenance checks for the LLM Wiki."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
RAW = ROOT / "raw"

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def iter_markdown_files(base: Path) -> list[Path]:
    return sorted(
        path
        for path in base.rglob("*.md")
        if path.is_file() and "templates" not in path.relative_to(ROOT).parts
    )


def local_target(link: str, source: Path) -> Path | None:
    if "://" in link or link.startswith("#") or link.startswith("mailto:"):
        return None

    target = link.split("#", 1)[0].strip()
    if not target:
        return None

    return (source.parent / target).resolve()


def check_links(files: list[Path]) -> list[str]:
    errors: list[str] = []

    for source in files:
        text = source.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = local_target(match.group(1), source)
            if target is None:
                continue
            if not target.exists():
                rel_source = source.relative_to(ROOT)
                errors.append(f"{rel_source}: broken link -> {match.group(1)}")

    return errors


def find_inbox_sources() -> list[Path]:
    inbox = RAW / "inbox"
    if not inbox.exists():
        return []
    return iter_markdown_files(inbox)


def main() -> int:
    files = iter_markdown_files(ROOT)
    errors = check_links(files)
    inbox_sources = find_inbox_sources()

    if errors:
        print("Broken links:")
        for error in errors:
            print(f"- {error}")
    else:
        print("No broken local Markdown links found.")

    if inbox_sources:
        print("\nInbox sources waiting for distillation:")
        for path in inbox_sources:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("No Markdown files waiting in raw/inbox.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
