from __future__ import annotations

from pathlib import Path
import re
import yaml

SECTION_MAP = {
    "国内政策": "policy",
    "国外前沿": "frontier",
    "重点新闻": "news",
}

REQUIRED_META = ("number", "date_start", "date_end", "lede", "pages_base_url", "next_label")


def parse_issue(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("issue.md must start with YAML front matter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("invalid front matter")
    meta = yaml.safe_load(parts[1]) or {}
    for key in REQUIRED_META:
        if key not in meta or meta[key] in (None, ""):
            raise ValueError(f"missing front matter field: {key}")
    body = parts[2].strip()
    sections = _parse_sections(body)
    expected = set(SECTION_MAP.values())
    got = {s["id"] for s in sections}
    if len(sections) != 3 or got != expected:
        raise ValueError(f"sections must be exactly 国内政策/国外前沿/重点新闻, got {got}")
    return {**meta, "sections": sections}


def _parse_sections(body: str) -> list[dict]:
    chunks = re.split(r"(?m)^## ", body)
    sections: list[dict] = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.splitlines()
        title = lines[0].strip()
        if title not in SECTION_MAP:
            raise ValueError(f"unknown section: {title}")
        items = _parse_items("\n".join(lines[1:]), section=title)
        sections.append({"id": SECTION_MAP[title], "title": title, "items": items})
    return sections


def _parse_items(body: str, section: str) -> list[dict]:
    parts = re.split(r"(?m)^### ", body)
    items: list[dict] = []
    for idx, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        lines = part.splitlines()
        title = lines[0].strip()
        fields: dict[str, str] = {}
        key = None
        acc: list[str] = []
        for line in lines[1:]:
            m = re.match(r"^- (\w+):\s*(.*)$", line)
            if m:
                if key is not None:
                    fields[key] = "\n".join(acc).strip()
                key = m.group(1)
                val = m.group(2)
                if val == "|":
                    acc = []
                else:
                    acc = [val]
            else:
                if key is not None:
                    acc.append(line)
        if key is not None:
            fields[key] = "\n".join(acc).strip()
        for req in ("source", "url", "summary"):
            if not fields.get(req):
                raise ValueError(f"{section} item[{len(items)}] missing {req}: {title}")
        if not fields["url"].startswith(("http://", "https://")):
            raise ValueError(f"{section} item[{len(items)}] invalid url: {title}")
        featured_raw = (fields.get("featured") or "").strip().lower()
        featured = featured_raw in ("true", "yes", "1")
        items.append(
            {
                "title": title,
                "source": fields["source"],
                "url": fields["url"],
                "summary": fields["summary"],
                "image": fields.get("image") or None,
                "featured": featured,
            }
        )
    if not items:
        raise ValueError(f"section {section} has no items")
    return items
