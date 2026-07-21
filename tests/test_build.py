from pathlib import Path
import shutil

from scripts.build import build_issue

FIXTURE = Path(__file__).parent / "fixtures" / "sample-issue.md"


def test_build_writes_html(tmp_path):
    issue_dir = tmp_path / "2026-07-01"
    issue_dir.mkdir()
    shutil.copy(FIXTURE, issue_dir / "issue.md")

    out = build_issue(issue_dir, site_root=tmp_path / "site")
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "人形脉冲" in html
    assert "国内政策" in html
    assert "section-policy" in html
    assert "@font-face" in html  # fonts.css inlined
    assert 'href="../../assets/fonts/fonts.css"' not in html

    email = issue_dir / "email.html"
    assert email.exists()
    email_html = email.read_text(encoding="utf-8")
    assert "在线阅读" in email_html
    assert "<table" in email_html

    site_issue = tmp_path / "site" / "issues" / "01" / "index.html"
    assert site_issue.exists()
    assert (tmp_path / "site" / "index.html").exists()
