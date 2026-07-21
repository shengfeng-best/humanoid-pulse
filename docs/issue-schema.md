# issue.md 字段说明

每期周报正文为单个 Markdown 文件，由 YAML front matter 与三节正文组成。

## Front matter（强制）

文件必须以 `---` 包裹的 YAML front matter 开头：

```yaml
---
number: 1
date_start: "2026-07-14"
date_end: "2026-07-20"
lede: "编者开篇八十到一百二十字。"
pages_base_url: "https://EXAMPLE.github.io/humanoid-pulse"
next_label: "№02"
---
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `number` | int | 期号，如 `1` 表示 №01 |
| `date_start` | string | 本期起始日期，`YYYY-MM-DD` |
| `date_end` | string | 本期结束日期，`YYYY-MM-DD` |
| `lede` | string | 编者开篇，80–120 字 |
| `pages_base_url` | string | GitHub Pages 站点根 URL |
| `next_label` | string | 下期预告标签，如 `№02` |

以上字段均为**强制**；缺失或为空时解析器抛出 `ValueError`。

## 正文三节（强制）

正文必须且只能包含以下三个二级标题各一次（顺序不限；重复标题或节数不为 3 时解析失败）：

| 标题 | section id |
|------|------------|
| 国内政策 | `policy` |
| 国外前沿 | `frontier` |
| 重点新闻 | `news` |

每节至少包含 **1 条** 条目。

## 条目格式

每条以三级标题 `### 条目标题` 开头，后跟 YAML 风格列表字段：

```markdown
### 条目标题
- source: 工信部
- url: https://example.com/a
- image: assets/optional.jpg
- summary: |
  短评第一句。
  短评第二句。
```

| 字段 | 强制 | 说明 |
|------|------|------|
| `source` | 是 | 来源署名（机构/媒体名） |
| `url` | 是 | 原文链接，须以 `http://` 或 `https://` 开头 |
| `summary` | 是 | 短评，2–4 句；可用 `\|` 多行块 |
| `image` | 否 | 配图相对路径，如 `assets/foo.jpg`；缺省为 `null` |

缺强制字段或 URL 不合法时，解析器抛出 `ValueError`，消息含节名、条目索引与字段名。

## 解析结果

`parse_issue(path)` 返回 dict，形状示例：

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
      "id": "policy",
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
