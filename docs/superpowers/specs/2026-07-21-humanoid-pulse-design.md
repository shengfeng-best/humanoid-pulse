# 人形脉冲 · PULSE — 设计规格

**日期：** 2026-07-21  
**状态：** 待实现（第一期手工出刊）  
**仓库：** `d:\cursor\humanoid-pulse\`（与 `kimi-opc` 平级、独立 Git）

---

## 1. 目标

每周一期具身智能 / 人形机器人洞察周报，以高质量、可追溯来源为先，产出：

1. **美学单页网页**（纸刊编辑风），托管于 GitHub Pages，可分享链接  
2. **同源邮件 HTML**，经 SMTP 发至：
   - `15639028969@163.com`
   - `shengfeng@openloong.net`

刊名采用期号制，例如：

> **人形脉冲 №01 · 2026.07.14–07.20**

---

## 2. 范围与非目标

### 本期（MVP）范围内

- 独立仓库脚手架：目录、模板、构建脚本、发信脚本、来源规范、`DESIGN.md`
- 第一期内容**人工精编**（质量优先），渲染网页 + 发信
- GitHub Pages 发布一期可访问链接
- 三栏结构、每条带原链、图文并茂（有可靠配图才配）

### 明确不做（后续再开）

- 全自动 RSS/爬虫采编流水线
- 订阅管理系统、退订页、多收件人运营后台
- PDF / 印刷分页（Paged.js 等）
- 依赖 Cloudflare Pages + Resend 全家桶（已选定 GitHub Pages + SMTP）

---

## 3. 内容结构

| 栏目 | 目标条数 | 说明 |
|------|----------|------|
| 01 · 国内政策 | 3–4 | 部委、地方配套、产业政策与试点 |
| 02 · 国外前沿 | 3–4 | 实验室、顶会顶刊、海外头部产品/演示 |
| 03 · 重点新闻 | 6–8 | 国内外产业与交付向硬新闻 |

**单条字段（强制）：**

- 标题（可点击，指向原文 URL）
- Claude 式短评（2–4 句：事实 + 判断，不灌水）
- 来源署名（机构/媒体名）
- 原文链接（http/https，须可访问）
- 配图（可选：仅当来源官方或可合理引用时）

**开篇：** 编者按 80–120 字，给出本周「脉冲」判断，不堆清单。

---

## 4. 质量闸门（来源）

只收录满足以下之一的来源，否则不进刊：

- 中国政府 / 部委 / 地方政府正式发布与权威通稿
- 央媒与一线专业科技媒体的可核验报道（须能回溯到更一手出处时优先一手）
- 顶会、顶刊、预印本平台上的论文或官方会议材料
- 一线厂商、实验室、开源项目的**官方**博客 / 新闻稿 / GitHub Release

**禁止：** 无出处传闻、营销软文无事实核验、聚合站二手改写且无法回链原文。

来源白名单与操作细则维护在仓库 `docs/sources.md`。

---

## 5. 视觉与排版

### 5.1 方向（已确认）

**A · 纸刊编辑风**

- 暖纸底、衬线刊头、安静可读
- 单栏长页；科技感来自层级与节奏，不用霓虹、重阴影、紫渐变堆料
- 短评语气：克制、锋利，接近 Claude 式编辑腔

### 5.2 页面信息架构（已确认）

1. 刊头：`PULSE · №xx` + 日期区间  
2. 大标题「人形脉冲」+ 编者开篇  
3. 三栏锚点：01 / 02 / 03  
4. 分节条目流：标题链 · 短评 · 来源 · 可选配图（有图才图文并排）  
5. 页脚：GitHub Pages 在线链接 + 下期预告  

### 5.3 排版技术选型

| 采用 | 用途 |
|------|------|
| 自研 `templates/pulse.html` | 网页主模板；视觉语法**参考** [tufte-css](https://github.com/edwardtufte/tufte-css)（栏宽、字阶、留白、克制强调色），不整仓 fork |
| [fontsource](https://github.com/fontsource/fontsource) | 自托管西文衬线 + **Noto Serif SC / 思源宋体** 等 CJK，避免外链字体不稳定 |
| 仓库根 `DESIGN.md` | 颜色、字阶、间距、组件规则；保证每期生成一致 |

| 不采用（本期） | 原因 |
|----------------|------|
| Paged.js / Postext | 偏印刷分页，邮件不友好，MVP 过重 |
| typography.js | 对中文周报收益有限 |
| laughing-man + Resend | 与已定 SMTP / Pages 栈重复 |

**邮件版：** 同源色板与文案；布局改为邮箱兼容的 table 简化版（`email.html`），文首固定插入 Pages 在线阅读链接。

---

## 6. 架构与目录

```
humanoid-pulse/
├── README.md
├── DESIGN.md                 # 视觉系统契约
├── docs/
│   ├── sources.md            # 来源白名单与采编规范
│   └── superpowers/specs/    # 本设计文档
├── issues/
│   └── YYYY-MM-№NN/
│       ├── issue.md          # 可编辑正文（链接、短评、图）
│       ├── assets/           # 本期配图
│       ├── issue.html        # 网页完整版
│       └── email.html        # 邮件兼容版
├── templates/
│   ├── pulse.html            # 网页模板
│   └── pulse-email.html      # 邮件模板
├── scripts/
│   ├── build.py              # issue.md → issue.html + email.html
│   └── send_email.py         # SMTP 发送
├── .env.example              # SMTP 变量示例（真密钥不进库）
├── .gitignore
└── docs/site/                # GitHub Pages 站点根（仓库 Settings → Pages → /docs/site）
    ├── index.html            # 指向最新一期或索引
    └── issues/№NN/index.html # 由 build 同步自 issues/.../issue.html
```

**Pages 约定（唯一）：** 使用 GitHub Pages，发布目录为 `docs/site/`。构建脚本在生成 `issues/.../issue.html` 后，同步一份到 `docs/site/issues/№NN/index.html`，并更新 `docs/site/index.html` 指向最新期。

### 数据流

```
issue.md（人工精编）
    → build.py + templates + DESIGN.md
    → issue.html + email.html
    → 同步至 docs/site/ → git push → Pages URL
    → send_email.py → 两收件人
```

### 配置（环境变量，不进 Git）

- `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASS`
- `SMTP_FROM`（显示发件人）
- `PULSE_TO`（默认两个邮箱，可用逗号分隔覆盖）

---

## 7. 错误处理

- **构建：** `issue.md` 缺强制字段（标题/链接/短评）则失败并指出条目  
- **链接：** 构建时可选做 HEAD/GET 可达性检查；失败则警告，默认不阻断出刊（人工可 `--strict`）  
- **发信：** SMTP 认证失败立即退出非零；部分收件人失败则日志标明并非零退出  
- **配图：** 缺失或无法加载时降级为纯文字条目，不留破图框  

---

## 8. 第一期执行约定

- 模式：**C — 先手工跑通**（本规格已锁定）  
- 产出 №01 完整网页 + 邮件发送  
- 自动化采编不在第一期交付内；日后若加，仍必须经过第 4 节质量闸门  

---

## 9. 成功标准

1. 本地打开 `issue.html` 呈现纸刊风三栏长页，移动端可读  
2. GitHub Pages 给出可公开访问的 №01 URL  
3. 两邮箱收到图文 HTML，文内含原链与 Pages 链接  
4. 每条新闻均可回溯到来源页；无「空短评 / 无链接」条目  
5. 仓库无明文 SMTP 密码  

---

## 10. 决策记录

| 决策 | 选择 |
|------|------|
| 运行方式 | 独立项目；第一期手工，后续可半自动 |
| 交付形态 | Pages 链接 + 完整邮件 HTML |
| 托管 | GitHub Pages |
| 发信 | SMTP 脚本 |
| 刊名 | 人形脉冲 №（期号制） |
| 体量 | 加厚：政策 3–4 / 前沿 3–4 / 重点 6–8 |
| 仓库位置 | `d:\cursor\humanoid-pulse\`（与 kimi-opc 平级） |
| 视觉 | A · 纸刊编辑风 |
| 排版辅助 | Tufte 语法参考 + Fontsource + DESIGN.md |
