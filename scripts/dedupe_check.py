from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STORY_RE = re.compile(r"^- story:\s*(.+)$", re.MULTILINE)


def _extract_stories(issue_md: Path, *, require_all: bool = False) -> list[tuple[str, str]]:
    """Return (story_key, item_title) pairs from issue.md body."""
    text = issue_md.read_text(encoding="utf-8")
    if "---" in text:
        parts = text.split("---", 2)
        body = parts[2] if len(parts) >= 3 else text
    else:
        body = text

    stories: list[tuple[str, str]] = []
    chunks = re.split(r"(?m)^### ", body)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.splitlines()
        title = lines[0].strip()
        if not title or title.startswith("##"):
            continue
        m = STORY_RE.search(chunk)
        if not m:
            if require_all:
                raise SystemExit(f"{issue_md}: missing story: for item {title!r}")
            continue
        key = m.group(1).strip()
        if not key:
            if require_all:
                raise SystemExit(f"{issue_md}: empty story: for item {title!r}")
            continue
        stories.append((key, title))
    return stories


def check_issue(issue_dir: Path) -> None:
    issue_dir = Path(issue_dir)
    issue_md = issue_dir / "issue.md"
    if not issue_md.is_file():
        raise SystemExit(f"issue.md not found: {issue_md}")

    current = _extract_stories(issue_md, require_all=True)
    seen_local: set[str] = set()
    for key, title in current:
        if key in seen_local:
            raise SystemExit(f"duplicate story within {issue_dir.name}: {key!r} ({title})")
        seen_local.add(key)

    issues_root = REPO_ROOT / "issues"
    prior: dict[str, str] = {}
    for other in sorted(issues_root.iterdir()):
        if not other.is_dir() or other.resolve() == issue_dir.resolve():
            continue
        other_md = other / "issue.md"
        if not other_md.is_file():
            continue
        for key, title in _extract_stories(other_md, require_all=False):
            prior[key] = f"{other.name}/{title}"

    for key, title in current:
        if key in prior:
            raise SystemExit(
                f"duplicate story across issues: {key!r} "
                f"(this: {issue_dir.name}/{title}; prior: {prior[key]})"
            )

    print(f"dedupe OK: {len(current)} stories in {issue_dir.name}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Verify unique story: keys in Pulse issues")
    parser.add_argument("issue_dir", type=Path, help="Path to issue directory")
    args = parser.parse_args(argv)
    try:
        check_issue(args.issue_dir)
    except SystemExit as exc:
        if exc.code:
            sys.exit(exc.code)


if __name__ == "__main__":
    main()
