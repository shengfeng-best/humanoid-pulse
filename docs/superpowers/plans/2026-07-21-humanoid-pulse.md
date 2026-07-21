# 人形脉冲 · PULSE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建独立周报仓库，用纸刊风模板把人工精编的 `issue.md` 渲染成网页 + 邮件 HTML，经 GitHub Pages 发布，并用 SMTP 发到两个指定邮箱；完成 №01 出刊。

**Architecture:** Markdown 一期一文 → Python `build.py` 解析并套 `templates/pulse.html` / `pulse-email.html` → 写出 `issues/.../issue.html` + `email.html` 并同步到 `docs/site/` → `send_email.py` 读 `.env` 发信。第一期内容人工检索高质量来源撰写，不做自动采编。

**Tech Stack:** Python 3.11+（标准库 + PyYAML）、自研 HTML 模板（Tufte 语法参考）、Fontsource 自托管字体（Noto Serif SC + Source Serif 4）、GitHub Pages、SMTP（stdlib `smtplib`）、pytest

## Global Constraints

- 仓库根：`d:\cursor\humanoid-pulse\`（与 kimi-opc 平级）
- 刊名格式：`人形脉冲 №NN · YYYY.MM.DD–MM.DD`
- 栏目与体量：国内政策 3–4、国外前沿 3–4、重点新闻 6–8
- 每条强制：标题、短评、来源、原文 URL；配图可选
- 收件人默认：`15639028969@163.com,shengfeng@openloong.net`
- SMTP 密钥只进 `.env`，永不提交
- Pages 发布目录唯一：`docs/site/`
- 视觉：纸刊编辑风（暖纸底、衬线刊头）；禁止紫渐变霓虹堆料
- 不做：自动爬虫、Resend/Cloudflare 全家桶、Paged.js

## File Map

| 路径 | 职责 |
|------|------|
| `DESIGN.md` | 颜色、字阶、组件规则（构建/人工都参照） |
| `docs/sources.md` | 来源白名单与采编闸门 |
| `docs/issue-schema.md` | `issue.md` 字段说明 |
| `templates/pulse.html` | 网页完整版模板（`{{placeholders}}`） |
| `templates/pulse-email.html` | 邮件 table 布局模板 |
| `assets/fonts/` | 自托管 woff2 |
| `scripts/parse_issue.py` | 解析 `issue.md` → 结构化 dict |
| `scripts/build.py` | 渲染 HTML + 同步 Pages |
| `scripts/send_email.py` | SMTP 发信 |
| `scripts/vendor_fonts.py` | 从 Fontsource 拉取/复制字体到 `assets/fonts/` |
| `tests/test_parse_issue.py` | 解析与校验测试 |
| `tests/test_build.py` | 构建输出冒烟测试 |
| `tests/fixtures/sample-issue.md` | 最小合法样例 |
| `issues/2026-07-01/issue.md` | №01 正文（目录名用 ASCII，避免 № 进路径） |
| `issues/2026-07-01/assets/` | №01 配图 |
| `.env.example` | SMTP 变量模板 |
| `README.md` | 使用说明 |
| `requirements.txt` | `PyYAML`、`pytest` |

**路径约定：** 规格中的 `YYYY-MM-№NN` 在文件系统落地为 `issues/YYYY-MM-NN/`（两位期号，如 `2026-07-01`）；页面与邮件文案仍显示 `№01`。

---

### Task 1: 脚手架与 issue 解析器

**Files:**
- Create: `requirements.txt`
- Create: `docs/issue-schema.md`
- Create: `scripts/parse_issue.py`
- Create: `tests/fixtures/sample-issue.md`
- Create: `tests/test_parse_issue.py`
- Modify: `.gitignore`（若缺 `.env` / `__pycache__` / `.venv`）

**Interfaces:**
- Produces: `parse_issue(path: Path) -> dict` 形状见下方；缺强制字段时 `raise ValueError`（消息含条目索引与字段名）

`issue.md` 约定格式：

```markdown
---
number: 1
date_start: "2026-07-14"
date_end: "2026-07-20"
lede: "编者开篇八十到一百二十字。"
pages_base_url: "https://EXAMPLE.github.io/humanoid-pulse"
next_label: "№02"
---

## 国内政策

### 条目标题
- source: 工信部
- url: https://example.com/a
- image: assets/optional.jpg
- summary: |
  短评第一句。
  短评第二句。

## 国外前沿

### ...

## 重点新闻

### ...
```

解析结果 dict：

```python
{
  "number": 1,
  "date_start": "2026-07-14",
  "date_end": "2026-07-20",
  "lede": "...",
  "pages_base_url": "...",
  "next_label": "№02",
  "sections": [
    {
      "id": "policy",          # policy | frontier | news
      "title": "国内政策",
      "items": [
        {
          "title": "...",
          "source": "...",
          "url": "https://...",
          "summary": "...",
          "image": "assets/..." | None
        }
      ]
    }
  ]
}
```

- [ ] **Step 1: 写依赖与 schema 文档**

`requirements.txt`:

```
PyYAML>=6.0.1
pytest>=8.0.0
```

`docs/issue-schema.md`：把上面格式与三节标题必须为「国内政策」「国外前沿」「重点新闻」写清楚；强制字段列出。

- [ ] **Step 2: 写失败测试**

`tests/fixtures/sample-issue.md`：含完整 front matter + 每节至少 1 条合法条目。

`tests/test_parse_issue.py`:

```python
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

def test_missing_url_raises():
    bad = FIXTURE.parent / "bad-issue.md"
    bad.write_text(
        "---\nnumber: 1\ndate_start: '2026-07-14'\ndate_end: '2026-07-20'\n"
        "lede: 'x' * 80\npages_base_url: 'https://example.com'\nnext_label: '№02'\n---\n\n"
        "## 国内政策\n\n### 标题\n- source: 测试\n- summary: 短评\n\n"
        "## 国外前沿\n\n### 标题2\n- source: 测试\n- url: https://ex.com\n- summary: 短评\n\n"
        "## 重点新闻\n\n### 标题3\n- source: 测试\n- url: https://ex.com\n- summary: 短评\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="url"):
        parse_issue(bad)
```

注意：`lede` 一行写成真实 80+ 字中文，勿用 `'x' * 80` 字面进 front matter；测试里用合法 YAML 字符串。

- [ ] **Step 3: 运行测试确认失败**

Run: `cd /d/cursor/humanoid-pulse && python -m pip install -r requirements.txt && python -m pytest tests/test_parse_issue.py -v`

Expected: FAIL（`ModuleNotFoundError: scripts.parse_issue` 或类似）

- [ ] **Step 4: 实现 `scripts/parse_issue.py`**

```python
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
    if got != expected:
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
        items.append(
            {
                "title": title,
                "source": fields["source"],
                "url": fields["url"],
                "summary": fields["summary"],
                "image": fields.get("image") or None,
            }
        )
    if not items:
        raise ValueError(f"section {section} has no items")
    return items
```

在 `scripts/` 下增加空 `__init__.py`，保证 `python -m pytest` 可导入；或在 `pytest.ini` 设 `pythonpath = .`。

`pytest.ini`:

```
[pytest]
pythonpath = .
testpaths = tests
```

- [ ] **Step 5: 跑通测试**

Run: `python -m pytest tests/test_parse_issue.py -v`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add requirements.txt pytest.ini docs/issue-schema.md scripts/parse_issue.py scripts/__init__.py tests/ .gitignore
git commit -m "feat: add issue.md parser and schema"
```

---

### Task 2: DESIGN.md、字体与网页/邮件模板

**Files:**
- Create: `DESIGN.md`
- Create: `scripts/vendor_fonts.py`
- Create: `assets/fonts/.gitkeep`（及生成的 woff2）
- Create: `templates/pulse.html`
- Create: `templates/pulse-email.html`

**Interfaces:**
- Consumes: DESIGN tokens（颜色名见下）
- Produces: 模板占位符集合（构建脚本必须使用同一套名字）

占位符（网页与邮件共用语义）：

- `{{number_padded}}` → `01`
- `{{date_range}}` → `2026.07.14–07.20`
- `{{lede}}`
- `{{pages_url}}` → 本期完整 Pages URL
- `{{next_label}}`
- `{{sections_html}}` → 已渲染分节 HTML 片段

- [ ] **Step 1: 写 `DESIGN.md`**

必须包含（写死这些值，勿改名）：

```markdown
# DESIGN.md — 人形脉冲

## Color
- --paper: #F4F1EA
- --ink: #1A1A1A
- --muted: #5C574F
- --rule: #D9D2C5
- --accent: #9A6350
- --source: #8A847C

## Type
- Display: "Noto Serif SC", "Source Serif 4", Georgia, serif
- UI: system-ui, sans-serif
- Title: 42px / 1.1
- Item title: 20px / 1.35
- Body: 15px / 1.65
- Meta: 11px / letter-spacing 0.16em

## Layout
- Max width: 720px
- Item with image: 1.4fr / 1fr grid
- No cards-as-decoration; hairline rules only
- Accent used only for section labels and sparse emphasis
```

- [ ] **Step 2: 实现字体托管脚本**

`scripts/vendor_fonts.py`：若本机有 `npm`，执行：

```bash
npm pack @fontsource/noto-serif-sc @fontsource/source-serif-4
```

解压并把拉丁 + 中文常用 subset 的 `woff2` 复制到 `assets/fonts/`。若无 npm，则用 urllib 从 jsDelivr 下载对应 woff2（URL 写死在脚本注释中），失败则退出非零并提示。

至少落地：

- `assets/fonts/noto-serif-sc-latin-400-normal.woff2`（或 chinese-simplified 子集）
- `assets/fonts/source-serif-4-latin-400-normal.woff2`

并生成 `assets/fonts/fonts.css` 含 `@font-face`。

- [ ] **Step 3: 写 `templates/pulse.html`**

完整 HTML5 文档：引入相对路径 `../../assets/fonts/fonts.css`（构建时改为相对输出目录正确的路径，或由 build 内联 `fonts.css`）。推荐 **build 时内联 fonts.css 文本**，图片仍用相对 `assets/`。

结构顺序：刊头 → 标题 → lede → 三锚点 → `{{sections_html}}` → 页脚（Pages 链接 + 下期）。

CSS 使用 DESIGN.md 变量；暖纸底；衬线标题；条目有 `image` 时图文并排，无图则单栏。

- [ ] **Step 4: 写 `templates/pulse-email.html`**

- 最外层 `<table width="100%">`，内宽 600px  
- 文首第一行：`在线阅读：{{pages_url}}`  
- 内联 style（邮箱不依赖外链 CSS）  
- 配图用绝对或 cid：第一期用 Pages 上的绝对图片 URL（`{{pages_base_url}}/issues/01/assets/...`），由 build 在渲染邮件时把相对 image 换成绝对 URL  

- [ ] **Step 5: 目视检查**

用临时字符串替换占位符，浏览器打开网页模板；邮件模板用浏览器打开检查不乱版。

- [ ] **Step 6: Commit**

```bash
git add DESIGN.md assets/fonts templates scripts/vendor_fonts.py
git commit -m "feat: add editorial templates and self-hosted fonts"
```

---

### Task 3: 构建脚本与 Pages 同步

**Files:**
- Create: `scripts/build.py`
- Create: `tests/test_build.py`
- Create: `docs/site/.gitkeep`

**Interfaces:**
- Consumes: `parse_issue(path) -> dict`；模板文件  
- Produces: `build_issue(issue_dir: Path, *, strict: bool = False) -> Path` 返回写出的 `issue.html` 路径；副作用写出 `email.html` 与 `docs/site/...`

- [ ] **Step 1: 写构建测试**

```python
from pathlib import Path
from scripts.build import build_issue

def test_build_writes_html(tmp_path, monkeypatch):
    # copy fixture issue into tmp_path / "2026-07-01"
    ...
    out = build_issue(issue_dir, site_root=tmp_path / "site")
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "人形脉冲" in html
    assert "国内政策" in html
    email = issue_dir / "email.html"
    assert email.exists()
    assert "在线阅读" in email.read_text(encoding="utf-8")
    assert (tmp_path / "site" / "issues" / "01" / "index.html").exists()
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m pytest tests/test_build.py -v`  
Expected: FAIL（build 未实现）

- [ ] **Step 3: 实现 `scripts/build.py`**

核心逻辑：

1. `data = parse_issue(issue_dir / "issue.md")`  
2. `number_padded = f"{int(data['number']):02d}"`  
3. `date_range` 格式化：`2026.07.14–07.20`（结束日若同年同月则缩写月日）  
4. `pages_url = f"{data['pages_base_url'].rstrip('/')}/issues/{number_padded}/"`  
5. 渲染 `sections_html`：按 DESIGN 规则生成分节与条目（转义 HTML：`html.escape`）  
6. 若 `image` 路径存在则嵌入 `<img>`；不存在则跳过图片且不留破图  
7. 读模板，替换占位符，写 `issue_dir/issue.html` 与 `issue_dir/email.html`  
8. 复制/写入 `site_root/issues/{number_padded}/index.html`，复制 `assets/` 到同级  
9. 写/更新 `site_root/index.html`：标题列表链接到最新期  
10. CLI：`python scripts/build.py issues/2026-07-01`；支持 `--strict`（预留：对 url 做请求，非 2xx 则失败）

```python
def build_issue(issue_dir: Path, site_root: Path | None = None, strict: bool = False) -> Path:
    ...
```

默认 `site_root = Path(__file__).resolve().parents[1] / "docs" / "site"`。

- [ ] **Step 4: 测试通过**

Run: `python -m pytest tests/test_build.py tests/test_parse_issue.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/build.py tests/test_build.py docs/site
git commit -m "feat: build issue.html email.html and Pages sync"
```

---

### Task 4: SMTP 发信脚本

**Files:**
- Create: `.env.example`
- Create: `scripts/send_email.py`
- Create: `tests/test_send_email.py`（mock `smtplib`）

**Interfaces:**
- Consumes: 环境变量 `SMTP_HOST` `SMTP_PORT` `SMTP_USER` `SMTP_PASS` `SMTP_FROM`；可选 `PULSE_TO`  
- Produces: `send_issue_email(email_html_path: Path, subject: str, to: list[str] | None = None) -> None`；失败 `SystemExit` 或抛错

- [ ] **Step 1: 写 `.env.example`**

```
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=
SMTP_PASS=
SMTP_FROM=人形脉冲 <your@example.com>
PULSE_TO=15639028969@163.com,shengfeng@openloong.net
```

- [ ] **Step 2: 写 mock 测试**

断言：调用 `SMTP_SSL`（465）或 `SMTP`+`starttls`；`sendmail` 被调用；缺 `SMTP_PASS` 时 raise。

- [ ] **Step 3: 实现 `send_email.py`**

- 用 `email.message.EmailMessage`，`set_content` 纯文本摘要 + `add_alternative(html, subtype="html")`  
- 主题：`人形脉冲 №{n} · {date_range}`  
- 默认收件人两个邮箱  
- 从 `issue_dir` 旁的 `email.html` 读取  
- CLI：`python scripts/send_email.py issues/2026-07-01`  
- 加载 `.env`：可用极简解析（勿强制加 python-dotenv；若加则写入 requirements）

- [ ] **Step 4: 测试通过并 Commit**

```bash
git add .env.example scripts/send_email.py tests/test_send_email.py
git commit -m "feat: add SMTP mailer for Pulse issues"
```

---

### Task 5: 文档与 README

**Files:**
- Create: `docs/sources.md`
- Create: `README.md`

- [ ] **Step 1: 写 `docs/sources.md`**

列出允许来源类别（与规格第 4 节一致）+ 操作清单：每条必须可点回原文；优先一手；禁止聚合站无出处。

- [ ] **Step 2: 写 `README.md`**

含：刊名说明、目录、如何写 `issue.md`、`build` / `send` 命令、Pages 设置（Settings → Pages → Deploy from branch → `/docs` 不行则说明需用 GitHub Action 指向 `docs/site`，**或**把 Pages 设为 `/docs` 且将 site 内容放在 `docs/` 根——若冲突，采用 **GitHub Action `peaceiris/actions-gh-pages` 发布 `docs/site`** 的 workflow 文件）。

为消除歧义，本任务同时创建：

`/.github/workflows/pages.yml`：push 到 `master` 时上传 `docs/site` 为 Pages artifact（`actions/upload-pages-artifact` + `actions/deploy-pages`）。

- [ ] **Step 3: Commit**

```bash
git add docs/sources.md README.md .github/workflows/pages.yml
git commit -m "docs: add sources guide README and Pages workflow"
```

---

### Task 6: 精编 №01 内容并构建

**Files:**
- Create: `issues/2026-07-01/issue.md`
- Create: `issues/2026-07-01/assets/`（有可靠配图才放）
- Generate: `issues/2026-07-01/issue.html`、`email.html`、`docs/site/**`

**Interfaces:**
- Consumes: Task 1–3 工具链；真实可核验 URL（WebSearch / 官方站）
- Produces: 完整 №01

- [ ] **Step 1: 检索 2026-07-14–07.20 周期内具身/人形新闻**

用 WebSearch / 官方站点，按三栏凑齐加厚体量；**每条记下可打开的原链**；无把握的丢弃。

- [ ] **Step 2: 撰写 `issue.md`**

- `number: 1`  
- `pages_base_url`: 先写占位 `https://<github-user>.github.io/humanoid-pulse`，创建远程仓库后改成真实值并重建  
- lede 80–120 字，Claude 式判断  
- 每条短评 2–4 句  

- [ ] **Step 3: 构建**

Run: `python scripts/build.py issues/2026-07-01`  
Expected: 生成 html；本地浏览器打开 `issues/2026-07-01/issue.html` 检查纸刊风与三栏。

- [ ] **Step 4: Commit 内容与构建产物**

```bash
git add issues/2026-07-01 docs/site
git commit -m "content: publish Humanoid Pulse №01"
```

---

### Task 7: 远程仓库、Pages 上线、SMTP 实发

**Files:**
- Modify: `issues/2026-07-01/issue.md`（真实 `pages_base_url`）
- Create: 用户本机 `.env`（不提交）

- [ ] **Step 1: 创建 GitHub 空仓库 `humanoid-pulse` 并 push**

```bash
gh repo create humanoid-pulse --public --source=d:/cursor/humanoid-pulse --remote=origin --push
```

（若 `gh` 不可用：用户在网页建库后 `git remote add` + `push`）

- [ ] **Step 2: 启用 Pages**

按 Task 5 workflow 启用 GitHub Pages；拿到 `https://<user>.github.io/humanoid-pulse/`。

- [ ] **Step 3: 回写 `pages_base_url` 并重建、再 push**

- [ ] **Step 4: 配置 `.env` 并实发**

向用户索取 SMTP（推荐 163 授权码）；写入 `.env`；执行：

```bash
python scripts/send_email.py issues/2026-07-01
```

Expected: 两邮箱收到邮件；含原链与在线阅读 URL。

- [ ] **Step 5: 验收对照规格第 9 节勾选；最终 commit 仅含 URL 修正（无 `.env`）**

```bash
git add issues/2026-07-01 docs/site
git commit -m "fix: set production Pages URL for №01"
git push
```

---

## Spec Coverage Checklist

| 规格项 | 任务 |
|--------|------|
| 独立仓库 + 目录结构 | 1–5 |
| 纸刊风网页 + 三栏 IA | 2–3, 6 |
| 邮件 HTML + 双收件人 SMTP | 4, 7 |
| GitHub Pages | 3, 5, 7 |
| 来源质量闸门文档 | 5；内容执行在 6 |
| DESIGN.md + Tufte 参考 + Fontsource | 2 |
| 第一期手工精编 | 6–7 |
| 无明文密码 | 4, 7 |
| 构建缺字段失败 | 1 |
| 配图缺失降级 | 3 |

## Placeholder / Consistency Review

- 文件系统期号目录统一 `issues/YYYY-MM-NN/`，展示用 `№NN`  
- 解析器与模板占位符名称在 Task 1–3 对齐  
- Pages：`docs/site` + Actions 发布，避免与「/docs 根」歧义  
