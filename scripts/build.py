from __future__ import annotations

import argparse
import html
import re
import shutil
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from scripts.parse_issue import parse_issue

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_ROOT = REPO_ROOT / "docs" / "site"
TEMPLATES = REPO_ROOT / "templates"
FONTS_CSS = REPO_ROOT / "assets" / "fonts" / "fonts.css"

SECTION_ORDER = ("policy", "frontier", "news")


def format_date_range(date_start: str, date_end: str) -> str:
    start = date.fromisoformat(date_start)
    end = date.fromisoformat(date_end)
    start_s = f"{start.year}.{start.month:02d}.{start.day:02d}"
    if start.year == end.year and start.month == end.month:
        end_s = f"{end.month:02d}.{end.day:02d}"
    elif start.year == end.year:
        end_s = f"{end.month:02d}.{end.day:02d}"
    else:
        end_s = f"{end.year}.{end.month:02d}.{end.day:02d}"
    return f"{start_s}–{end_s}"


def _rewrite_font_urls(css: str) -> str:
    """Point @font-face urls at site/repo assets/fonts from issues/NN/ pages."""
    return re.sub(r'url\("\./([^"]+)"\)', r'url("../../assets/fonts/\1")', css)


def _inline_fonts(template: str) -> str:
    css = _rewrite_font_urls(FONTS_CSS.read_text(encoding="utf-8"))
    link = '<link rel="stylesheet" href="../../assets/fonts/fonts.css" />'
    return template.replace(link, f"<style>\n{css}\n  </style>")


def _render_web_sections(sections: list[dict], issue_dir: Path) -> str:
    by_id = {s["id"]: s for s in sections}
    parts: list[str] = []
    for sid in SECTION_ORDER:
        section = by_id[sid]
        items_html: list[str] = []
        for item in section["items"]:
            img_html = ""
            img_rel = item.get("image")
            has_image = bool(img_rel) and (issue_dir / img_rel).is_file()
            item_class = "item item--with-image" if has_image else "item"
            if has_image:
                src = html.escape(img_rel, quote=True)
                alt = html.escape(item["title"], quote=True)
                img_html = f'\n      <img class="item-image" src="{src}" alt="{alt}" />'
            title = html.escape(item["title"])
            url = html.escape(item["url"], quote=True)
            summary = html.escape(item["summary"]).replace("\n", "<br />\n")
            source = html.escape(item["source"])
            items_html.append(
                f'<article class="{item_class}">\n'
                f'  <div class="item-body">\n'
                f'    <h3 class="item-title"><a href="{url}">{title}</a></h3>\n'
                f'    <p class="item-summary">{summary}</p>\n'
                f'    <p class="item-source">{source}</p>\n'
                f"  </div>{img_html}\n"
                f"</article>"
            )
        title_esc = html.escape(section["title"])
        parts.append(
            f'<section class="section" id="section-{sid}">\n'
            f'  <h2 class="section-label">{title_esc}</h2>\n'
            f'  {"".join(items_html)}\n'
            f"</section>"
        )
    return "\n\n".join(parts)


def _render_email_sections(
    sections: list[dict],
    issue_dir: Path,
    pages_base_url: str,
    number_padded: str,
) -> str:
    by_id = {s["id"]: s for s in sections}
    base = pages_base_url.rstrip("/")
    parts: list[str] = []
    for sid in SECTION_ORDER:
        section = by_id[sid]
        rows: list[str] = []
        title_esc = html.escape(section["title"])
        rows.append(
            f'<tr><td style="padding:24px 0 8px 0;font-family:system-ui,-apple-system,sans-serif;'
            f'font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#9A6350;'
            f'font-weight:600;">{title_esc}</td></tr>'
        )
        for item in section["items"]:
            title = html.escape(item["title"])
            url = html.escape(item["url"], quote=True)
            summary = html.escape(item["summary"]).replace("\n", "<br />")
            source = html.escape(item["source"])
            img_html = ""
            img_rel = item.get("image")
            if img_rel and (issue_dir / img_rel).is_file():
                abs_src = html.escape(
                    f"{base}/issues/{number_padded}/{img_rel.replace(chr(92), '/')}",
                    quote=True,
                )
                alt = html.escape(item["title"], quote=True)
                img_html = (
                    f'<p style="margin:0 0 12px 0;">'
                    f'<img src="{abs_src}" alt="{alt}" width="560" '
                    f'style="display:block;width:100%;max-width:560px;height:auto;border:0;" />'
                    f"</p>"
                )
            rows.append(
                f'<tr><td style="padding:16px 0 0 0;border-top:1px solid #D9D2C5;">'
                f'<p style="margin:0 0 8px 0;font-family:Georgia,\'Times New Roman\',serif;'
                f'font-size:18px;line-height:1.35;">'
                f'<a href="{url}" style="color:#1A1A1A;text-decoration:none;">{title}</a></p>'
                f"{img_html}"
                f'<p style="margin:0 0 8px 0;font-family:Georgia,\'Times New Roman\',serif;'
                f'font-size:15px;line-height:1.65;color:#1A1A1A;">{summary}</p>'
                f'<p style="margin:0;font-family:system-ui,-apple-system,sans-serif;'
                f'font-size:11px;letter-spacing:0.16em;color:#8A847C;">{source}</p>'
                f"</td></tr>"
            )
        parts.append(
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
            + "".join(rows)
            + "</table>"
        )
    return "".join(parts)


def _fill(template: str, mapping: dict[str, str]) -> str:
    out = template
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def _check_urls(data: dict) -> None:
    for section in data["sections"]:
        for item in section["items"]:
            url = item["url"]
            try:
                req = urllib.request.Request(url, method="HEAD")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if not (200 <= getattr(resp, "status", 200) < 300):
                        raise SystemExit(f"strict: non-2xx for {url}")
            except urllib.error.HTTPError as e:
                if not (200 <= e.code < 300):
                    raise SystemExit(f"strict: non-2xx for {url}: {e.code}") from e
            except Exception as e:
                raise SystemExit(f"strict: failed to fetch {url}: {e}") from e


def _sync_site(
    issue_html: str,
    issue_dir: Path,
    site_root: Path,
    number_padded: str,
    date_range: str,
) -> None:
    site_issue = site_root / "issues" / number_padded
    site_issue.mkdir(parents=True, exist_ok=True)
    (site_issue / "index.html").write_text(issue_html, encoding="utf-8")

    src_assets = issue_dir / "assets"
    dst_assets = site_issue / "assets"
    if src_assets.is_dir():
        if dst_assets.exists():
            shutil.rmtree(dst_assets)
        shutil.copytree(src_assets, dst_assets)

    fonts_src = REPO_ROOT / "assets" / "fonts"
    fonts_dst = site_root / "assets" / "fonts"
    if fonts_src.is_dir():
        fonts_dst.parent.mkdir(parents=True, exist_ok=True)
        if fonts_dst.exists():
            shutil.rmtree(fonts_dst)
        shutil.copytree(fonts_src, fonts_dst)

    index_path = site_root / "index.html"
    link = f"issues/{number_padded}/"
    title = f"人形脉冲 №{number_padded} · {date_range}"
    entry = f'<li><a href="{html.escape(link, quote=True)}">{html.escape(title)}</a></li>'
    if index_path.exists():
        existing = index_path.read_text(encoding="utf-8")
        if f"issues/{number_padded}/" in existing:
            # replace that li if present, else leave
            existing = re.sub(
                rf'<li><a href="issues/{number_padded}/">.*?</a></li>',
                entry,
                existing,
                count=1,
            )
            index_path.write_text(existing, encoding="utf-8")
            return
        # insert after opening <ul>
        if "<ul>" in existing:
            existing = existing.replace("<ul>", f"<ul>\n    {entry}", 1)
            index_path.write_text(existing, encoding="utf-8")
            return

    index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>人形脉冲</title>
  <style>
    body {{ margin: 0; background: #F4F1EA; color: #1A1A1A;
      font-family: Georgia, "Times New Roman", serif; padding: 2.5rem 1.25rem; }}
    h1 {{ font-weight: 400; font-size: 32px; }}
    ul {{ padding-left: 1.25rem; line-height: 1.8; }}
    a {{ color: #1A1A1A; }}
  </style>
</head>
<body>
  <h1>人形脉冲</h1>
  <ul>
    {entry}
  </ul>
</body>
</html>
"""
    index_path.write_text(index_html, encoding="utf-8")


def build_issue(
    issue_dir: Path,
    site_root: Path | None = None,
    strict: bool = False,
) -> Path:
    issue_dir = Path(issue_dir)
    site_root = Path(site_root) if site_root is not None else DEFAULT_SITE_ROOT

    data = parse_issue(issue_dir / "issue.md")
    if strict:
        _check_urls(data)

    number_padded = f"{int(data['number']):02d}"
    date_range = format_date_range(data["date_start"], data["date_end"])
    pages_url = f"{data['pages_base_url'].rstrip('/')}/issues/{number_padded}/"

    web_sections = _render_web_sections(data["sections"], issue_dir)
    email_sections = _render_email_sections(
        data["sections"], issue_dir, data["pages_base_url"], number_padded
    )

    mapping = {
        "number_padded": number_padded,
        "date_range": date_range,
        "lede": html.escape(data["lede"]),
        "pages_url": html.escape(pages_url, quote=True),
        "next_label": html.escape(data["next_label"]),
        "sections_html": web_sections,
    }

    web_tpl = _inline_fonts((TEMPLATES / "pulse.html").read_text(encoding="utf-8"))
    email_tpl = (TEMPLATES / "pulse-email.html").read_text(encoding="utf-8")

    issue_html = _fill(web_tpl, mapping)
    email_html = _fill(
        email_tpl,
        {**mapping, "sections_html": email_sections, "pages_url": pages_url},
    )

    out = issue_dir / "issue.html"
    out.write_text(issue_html, encoding="utf-8")
    (issue_dir / "email.html").write_text(email_html, encoding="utf-8")

    site_root.mkdir(parents=True, exist_ok=True)
    _sync_site(issue_html, issue_dir, site_root, number_padded, date_range)
    return out


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build Pulse issue HTML and sync Pages")
    parser.add_argument("issue_dir", type=Path, help="Path to issue directory")
    parser.add_argument(
        "--site-root",
        type=Path,
        default=None,
        help="GitHub Pages site root (default: docs/site)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="HEAD-check item URLs; fail on non-2xx",
    )
    args = parser.parse_args(argv)
    out = build_issue(args.issue_dir, site_root=args.site_root, strict=args.strict)
    print(out)


if __name__ == "__main__":
    main()
