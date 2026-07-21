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
- Max width: 1040px; text measure capped ~38em for long summaries
- Generous vertical rhythm: 2–2.5rem between items
- Cover: taller crop (~48vh), caption with hairline
- Featured: image full bleed then oversized title
- Item with image: 1.4fr / 1fr
- No cards; rules + typographic hierarchy carry the premium feel

## Imagery
- Prefer official press / vendor OG images; store under issues/.../assets/
- cover + per-item image optional; featured: true marks lead stories
