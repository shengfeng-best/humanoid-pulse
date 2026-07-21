# DESIGN.md — 人形脉冲

## Color
- --paper: #F3EFE6
- --ink: #141210
- --muted: #4F4A43
- --rule: #D4CBBC
- --accent: #8B5342
- --source: #7A746C
- --wash: #E7E0D3
- --surface: #FAF7F1

## Type
- Display: "Noto Serif SC", "Source Serif 4", Georgia, serif
- UI: system-ui, sans-serif
- Title: 60px / 1.05
- Featured title: 34px / 1.28
- Item title: 24px / 1.35
- Lede: 20px / 1.75
- Body: 18.5px / 1.8
- Meta: 12px / letter-spacing 0.14em

## Layout
- Desktop max width: ~1280–1320px（正文不再用 36em 收窄）
- Mobile root: ≥20px，单栏；禁止手机端缩小根字号
- Fluid type: clamp() 随屏宽缩放
- Item with image: 文宽图窄（约 1.55–1.65 / 0.85–0.9）

## Imagery
- Prefer official press / vendor OG images; store under issues/.../assets/
- cover + per-item image optional; featured: true marks lead stories
