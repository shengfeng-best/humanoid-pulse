# 人形脉冲 · PULSE

每周一期具身智能 / 人形机器人洞察周报。人工精编 Markdown → 纸刊风网页 + 邮件 HTML → GitHub Pages 发布 + SMTP 投递。

刊名示例：**人形脉冲 №01 · 2026.07.14–07.20**

## 目录

```
humanoid-pulse/
├── README.md
├── DESIGN.md                 # 视觉 token（颜色、字阶、版式）
├── docs/
│   ├── sources.md            # 来源质量闸门（采编必读）
│   ├── issue-schema.md       # issue.md 字段说明
│   └── site/                 # GitHub Pages 站点根（构建同步）
├── issues/YYYY-MM-NN/        # 各期源文件（NN = 两位期号）
│   ├── issue.md
│   ├── assets/
│   ├── issue.html            # build 生成
│   └── email.html            # build 生成
├── templates/                # 网页与邮件模板
├── scripts/
│   ├── parse_issue.py
│   ├── build.py
│   ├── send_email.py
│   └── vendor_fonts.py
├── tests/
└── .github/workflows/pages.yml
```

## 快速开始

### 环境

- Python 3.11+
- 依赖：`pip install -r requirements.txt`

### 撰写一期 `issue.md`

1. 新建目录 `issues/2026-07-01/`（路径用 ASCII 日期 + 期号，页面显示 `№01`）
2. 按 [docs/issue-schema.md](./docs/issue-schema.md) 编写 YAML front matter 与三节正文（国内政策 / 国外前沿 / 重点新闻）
3. 采编前阅读 [docs/sources.md](./docs/sources.md)，确保每条来源可核验
4. 可选配图放入 `issues/.../assets/`

最小示例见 [tests/fixtures/sample-issue.md](./tests/fixtures/sample-issue.md)。

### 构建

```bash
python scripts/build.py issues/2026-07-01
```

产出：

- `issues/2026-07-01/issue.html` — 本地预览完整版
- `issues/2026-07-01/email.html` — 邮件 HTML
- `docs/site/issues/01/index.html` — Pages 同步
- `docs/site/index.html` — 期号索引更新

可选严格模式（HEAD 检查所有 URL，失败则退出）：

```bash
python scripts/build.py issues/2026-07-01 --strict
```

### 发送邮件

1. 复制 `.env.example` 为 `.env`，填入 SMTP 配置（**勿提交 `.env`**）
2. 确保已构建 `email.html`
3. 发送：

```bash
python scripts/send_email.py issues/2026-07-01
```

默认收件人见 `.env.example` 中 `PULSE_TO`；主题格式为 `人形脉冲 №01 · 2026.07.14–07.20`。

### 测试

```bash
python -m pytest -v
```

## GitHub Pages

本站使用 **GitHub Actions** 发布 `docs/site/`，而非 Settings → Pages → Deploy from branch → `/docs`（避免与仓库 `docs/` 文档目录混淆）。

### 启用步骤

1. 将仓库 push 到 GitHub
2. **Settings → Pages → Build and deployment**
   - Source：**GitHub Actions**
3. 合并或 push 到 `master` 后，`.github/workflows/pages.yml` 自动：
   - 上传 `docs/site` 为 Pages artifact
   - 通过 `deploy-pages` 部署
4. 站点 URL：`https://<user>.github.io/humanoid-pulse/`
5. 在 `issue.md` 的 `pages_base_url` 填入该 URL（无尾斜杠），重新 `build` 并 push `docs/site`

### 出刊流程（摘要）

```bash
# 1. 编写 issue.md
# 2. 构建并检查
python scripts/build.py issues/2026-07-01
# 3. 提交内容与站点产物
git add issues/2026-07-01 docs/site
git commit -m "content: publish Humanoid Pulse №01"
git push
# 4. 配置 .env 后发信
python scripts/send_email.py issues/2026-07-01
```

## 相关文档

| 文档 | 内容 |
|------|------|
| [DESIGN.md](./DESIGN.md) | 纸刊风视觉规范 |
| [docs/issue-schema.md](./docs/issue-schema.md) | Markdown 格式与解析规则 |
| [docs/sources.md](./docs/sources.md) | 来源白名单与采编闸门 |
| [docs/superpowers/specs/2026-07-21-humanoid-pulse-design.md](./docs/superpowers/specs/2026-07-21-humanoid-pulse-design.md) | 完整设计规格 |

## 字体

首次克隆后若缺字体文件：

```bash
python scripts/vendor_fonts.py
```

## 许可与隐私

SMTP 密钥仅存本机 `.env`；仓库仅含 `.env.example` 模板。
