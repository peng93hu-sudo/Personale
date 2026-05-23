# Deck Structure — 33-Slide Reference Map

Slide-by-slide map of the reference deck (`data/template_wiseglow.pptx`), for
`build_deck.py`. 16:9, 33 slides, 25 native charts (18 line-with-markers,
7 clustered-column). Categories are usually the 12 months `1月…12月`.

## Conventions

- **Header** (top-left): `‹Section› · ‹nn› · ‹category›`
- **Footer**: `WiseGlow Italy · 资产运营 · GME PUN 深度分析 · ‹n›/33`
- **Stat cards**: big €/MWh number + short label; **annotations**: one line.
- Currency €/MWh throughout. Tag reconstructed curves with `· 代表性`.

## Front matter

| # | Title | Content / data |
|---|-------|----------------|
| 1 | Cover — `PUN 价格走势与峰谷套利 · DEEP DIVE 2024–2026` | 4 stat blocks (#charts, time span, price dims F0/F1/F2/F3, view); confidential footer + date |
| 2 | `00 · 方法论` | 4 source cards (GME / GSE / TERNA / 项目1) + 5 analysis dimensions |
| 3 | `00 · 目录` | Sections A–H with slide ranges (below) |

## A — PUN history (slides 4–8)

| # | Title | Chart | Data |
|---|-------|-------|------|
| 4 | PUN 月度走势 2024 | line | `PUN F0 2024` ×12 + 5 month annotations + full-year stats (mean/max/min/range/σ/CV) |
| 5 | PUN 月度走势 2025 | line | `PUN F0 2025` ×12 + annotations + stats |
| 6 | PUN 月度走势 2026 YTD | line | `PUN F0 2026` (partial) + YTD mean + YoY |
| 7 | 三年叠加对比 | line ×3 | 2024 / 2025 / 2026 YTD overlay + YoY deltas |
| 8 | PUN 统计特征 | clustered col | per-year max / mean / min + volatility commentary |

## B — Time-of-use F1/F2/F3 (slides 9–13)

| # | Title | Chart | Data |
|---|-------|-------|------|
| 9 | F1/F2/F3 定义 + 2024 基准 | line ×3 | F1/F2/F3 monthly 2024 + band defs + annual means |
| 10 | F1 日间峰 三年对比 | line ×3 | F1 2024/2025/2026 + annual means + events |
| 11 | F2 晚峰 三年对比 | line ×3 | F2 2024/2025/2026 + "new evening peak" note |
| 12 | F3 夜谷 三年对比 | line ×3 | F3 2024/2025/2026 + charging-window note |
| 13 | F2−F1 季节性倒挂 | clustered col | (F2−F1) monthly 2024/2025/2026 — BESS core signal |

## C — 7 zones (slides 14–17)

| # | Title | Chart | Data |
|---|-------|-------|------|
| 14 | 7 分区结构 + 年度均值 | clustered col | per-zone annual mean 2024/2025/2026 (7 zones) |
| 15 | 7 区域月度 2024 | line ×7 | each zone ×12 |
| 16 | 7 区域月度 2025 | line ×7 | each zone ×12 |
| 17 | 7 区域月度 2026 YTD | line ×7 | each zone (partial) + per-zone YTD cards |

Zones: NORD 北 · CNOR 中北 · CSUD 中南 · SUD 南 · CALA 卡拉布里亚 · SICI 西西里 · SARD 撒丁岛.

## D — Cross-zone spread (slides 18–20)

| # | Title | Chart | Data |
|---|-------|-------|------|
| 18 | 月度 最大−最小价差 | clustered col | monthly (max−min across zones) 2024/2025/2026 |
| 19 | NORD vs SARD | line ×2 + col | NORD & SARD monthly + (NORD−SARD) spread |
| 20 | SICI 孤岛溢价 | clustered col | (SICI−NORD) over 24 months |

## E — Intraday (slides 21–24)

| # | Title | Chart | Data |
|---|-------|-------|------|
| 21 | 冬季典型日内 (代表性) | line | 24h PUN, winter |
| 22 | 夏季鸭子曲线 (代表性) | line | 24h PUN, summer (duck curve) |
| 23 | 24h × 12月 热力图 | (shape grid) | 24×12 colour-banded cells (no native chart) |
| 24 | 15-min MTU | line ×2 | 60-min vs 15-min intraday window |

## F — Project-1 benchmarking (slides 25–28) — needs internal data

| # | Title | Chart | Data |
|---|-------|-------|------|
| 25 | 项目1 实际 vs 5 基准 | line ×5 | 项目1 realised vs CNOR / PUN F0 / F1 / F2, 11 months |
| 26 | 捕获率月度分解 | clustered col | capture rate % ×11 + mean |
| 27 | 光伏蚕食量化 | line ×2 | 项目1 price vs CNOR baseload + €/yr loss |
| 28 | BESS 加值情景 | (cards) | no-BESS / +1MW·2MWh / +2MW·4MWh scenarios |

## G — BESS arbitrage economics (slides 29–31) — needs assumptions

| # | Title | Chart | Data |
|---|-------|-------|------|
| 29 | 套利框架 (single-cycle) | (cards) | charge/discharge prices, Δ, €/cycle, €/yr |
| 30 | BESS 按区域对比 | (table) | 5 projects × {F2−F1, arbitrage, MACSE, MSD, total, reco} |
| 31 | 规模 × 时长矩阵 | (cards grid) | power × duration → revenue / CAPEX / payback |

## H — Conclusions (slides 32–33)

| # | Title | Content |
|---|-------|---------|
| 32 | 核心结论 Key Findings | 6 numbered findings (PUN↑, F2 new peak, zone spread, duck curve, Project-1 capture, BESS) |
| 33 | 行动路径 Next Steps | 5 timed actions (技术尽调 → 供应商 → 财务建模 → CDA 决策 → 市场监测) |

## Weekly variant (~6–8 slides)

Cover · A(latest month + WoW) · B(F1/F2/F3 latest) · C(7-zone snapshot) ·
D(key spread) · E(intraday) · takeaway. Reuse the same slide layouts; drop
the multi-year history and the F/G internal-data sections unless asked.
