from pathlib import Path
import pytest
from scripts.parse_issue import parse_issue

FIXTURE = Path(__file__).parent / "fixtures" / "sample-issue.md"


def test_parse_sample_has_three_sections():
    data = parse_issue(FIXTURE)
    assert data["number"] == 1
    assert len(data["sections"]) == 3
    assert data["sections"][0]["id"] == "policy"
    item = data["sections"][0]["items"][0]
    assert item["url"].startswith("http")
    assert item["summary"]
    assert item["source"]


def test_missing_url_raises(tmp_path):
    bad = tmp_path / "bad-issue.md"
    bad.write_text(
        "---\nnumber: 1\ndate_start: '2026-07-14'\ndate_end: '2026-07-20'\n"
        f"lede: {repr('x' * 80)}\n"
        "pages_base_url: 'https://example.com'\nnext_label: '№02'\n---\n\n"
        "## 国内政策\n\n### 标题\n- source: 测试\n- summary: 短评\n\n"
        "## 国外前沿\n\n### 标题2\n- source: 测试\n- url: https://ex.com\n- summary: 短评\n\n"
        "## 重点新闻\n\n### 标题3\n- source: 测试\n- url: https://ex.com\n- summary: 短评\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="url"):
        parse_issue(bad)
