# DESIGN.md — 人形脉冲

## Color
- --paper: #F4F1EA
- --ink: #1A1A1A
- --muted: #5C574F
- --rule: #D9D2C5
- --accent: #9A6350
- --source: #8A847C
- --wash: #EBE6DC

## Type
- Display: "Noto Serif SC", "Source Serif 4", Georgia, serif
- UI: system-ui, sans-serif
- Title: 48px / 1.08
- Featured title: 28px / 1.25
- Item title: 20px / 1.35
- Body: 16px / 1.7
- Meta: 11px / letter-spacing 0.16em

## Layout
- Max width: 960px
- Cover: full-bleed within wrap, 16:9–ish crop (~42vh max), caption under
- Featured item: stacked — image full width then text (magazine lead)
- Item with image: 1.35fr / 1fr grid (text / image)
- No cards-as-decoration; hairline rules + image rhythm
- Accent used for section labels and sparse emphasis

## Imagery
- Prefer official press / vendor OG images; store under issues/.../assets/
- cover + per-item image optional; featured: true marks lead stories
