---
name: italy-power-market-analysis
description: >-
  Generate the WiseGlow Italy GME / PUN power-market report deck — PUN price
  curves, F1/F2/F3 time-of-use bands, 7-zone spreads, intraday curves,
  Project-1 capture-rate benchmarking, and BESS peak/valley arbitrage
  economics. Produces a bilingual (中文-primary) PowerPoint in the WiseGlow
  house style (16:9, dark financial look). Use when the user asks to generate
  / refresh the market report or any of its pieces: "weekly PUN report",
  "monthly market update", "refresh GME / PUN data", "PUN 周报 / 月报",
  "GME 月度市场更新", "PUN 价格走势", "区域价差", "峰谷套利 / BESS 经济性",
  "italy power market", "prezzo unico nazionale". This skill is the data +
  deck engine that the `routines` skill calls for its "Monthly Market Update"
  and the market portion of "Weekly Review".
---

# Italy Power Market Analysis — GME / PUN Report Engine

Builds the WiseGlow Italy market-analysis deck from official Italian
electricity-market data. The reference output is a 33-slide bilingual deep
dive (cover → methodology → TOC → 8 analytical sections → conclusions), but
the skill is **scope-aware** and also produces shorter weekly / monthly
variants from the same pipeline and the same house style.

## When to use / not use

- **Use** for any GME / PUN market reporting: weekly refresh, monthly update,
  ad-hoc "what's the PUN doing", zone-spread questions, BESS arbitrage sizing.
- **Don't use** for non-market routines (morning brief, trip prep, CDA prep) —
  those live in the `routines` skill, which *calls* this skill when it needs
  market content.

## The pipeline (5 steps)

```
1. RESOLVE SCOPE   → weekly | monthly | full deep-dive (slide count + sections)
2. FETCH DATA      → source ladder (see references/data-sources.md)
3. COMPUTE METRICS → F1/F2/F3 bands, zone means, spreads, capture rate, arbitrage
4. BUILD DECK      → clone house template, replace chart data + text, re-date
5. DELIVER         → save dated .pptx to output/, (optional) email draft / Canva
```

Most runs are `scripts/fetch_market_data.py` → `scripts/build_deck.py`. Read
`references/data-sources.md` before step 2 and `references/deck-structure.md`
before step 4.

### Step 1 — Resolve scope

| Scope | Slides | Sections | Cadence |
|-------|--------|----------|---------|
| **Weekly** | ~6–8 | cover + A(latest) + B + C-snapshot + key spread + intraday + takeaway | Mon AM |
| **Monthly** | ~12–15 | + zone detail, spread evolution, Project-1 capture tracking | 1st week of month |
| **Full deep dive** | 33 | A–H complete (the reference deck) | quarterly / on demand |

Default to **weekly** unless the user says "月报 / monthly / 深度 / full".

### Step 2 — Fetch data (source ladder)

Italian market data is **network-gated** in Claude Code on the web (allowlist
policy). Pick the highest source the environment allows; see
`references/data-sources.md` for endpoints, tokens, and the exact allowlist.

1. **energy-charts.info** (Fraunhofer ISE) — hourly day-ahead per IT bidding
   zone. **No token.** Easiest engine for zonal + F1/F2/F3 + intraday.
2. **ENTSO-E Transparency** — authoritative hourly zonal day-ahead. Free token.
3. **GME official** (`mercatoelettrico.org` / FTP `MercatiElettrici/MGP_Prezzi`)
   — canonical PUN + zonal MGP XML. Terms-cookie or operator FTP credentials.
4. **Ember monthly (via GitHub raw)** — national **monthly** PUN, historical.
   Reachable even under the GitHub-only allowlist; use for backfill / sanity
   check. (This is the source whose 2024 values match the reference deck's
   `PUN F0`: Jan 99.14 … Dec 135.04.)

**Internal data the pipeline cannot fetch — the user must supply it:**
Project-1 monthly generation (MWh) + actual sale revenue (GSE settlement),
the 5-project → zone map (Marche/Lazio/Basilicata/Sicilia/Sardegna), and BESS
CAPEX / efficiency / MACSE / MSD assumptions. Keep these in
`data/internal_inputs.yaml`; never invent them.

**Why the data often comes up short — 3 stacked reasons (diagnose in this order):**
1. **Allowlist.** Under the default GitHub-only network policy, sources 1–3
   return **403**; only Ember (4) is reachable. Allowlisting their domains is
   what unlocks zonal / hourly data — see `references/data-sources.md`.
2. **Ember is narrow.** It carries only national **monthly** PUN (one point per
   month) and the GitHub snapshot lags (~previous year). It can fill the
   `PUN F0` backbone *only* — never F1/F2/F3, the 7 zones, or intraday, all of
   which need hourly data.
3. **Internal data is on no network.** Project-1 / BESS figures come from the
   user, full stop.
→ With no allowlist change, only `PUN F0` (monthly) is independently real;
sections B–G carry template figures until a higher source is opened.

### Step 3 — Compute metrics

From hourly zonal prices derive everything the deck shows:

- **Time-of-use bands** (Italian *fasce orarie*, ARERA):
  - **F1** day-peak — Mon–Fri 08:00–19:00
  - **F2** evening/shoulder — Mon–Fri 07–08 + 19–23, Sat 07–23
  - **F3** night/valley — nights + Sundays + holidays
  - **F0** = baseload average (this is the "PUN" headline series)
- **7 GME zones**: NORD, CNOR, CSUD, SUD, CALA, SICI, SARD.
- **Spreads**: F2−F1 (BESS seasonal signal), F1−F3 (total dynamic range),
  max−min cross-zone, NORD−SARD, SICI islanding premium.
- **Project-1 capture rate** = project realised €/MWh ÷ zone baseload.
- **Arbitrage** = (discharge price − charge price) × MWh × round-trip eff.

Logic + constants live in `scripts/metrics.py`. Band/zone definitions are
also in `references/deck-structure.md`.

### Step 4 — Build the deck (template-clone, not rebuild)

**Always clone the house template** (`data/template_wiseglow.pptx`) and
replace data — do **not** re-create slides from scratch. This guarantees the
exact house look (the theme is stock Office; the dark style is per-shape, so
rebuilding loses it).

`scripts/build_deck.py` uses python-pptx to: open the template, update each
chart via `chart.replace_data(...)`, rewrite the stat-card / annotation text
runs and the cover date + page footers, then save to
`output/WiseGlow_PUN_<YYYY-MM-DD>.pptx`. The slide↔data↔chart map is in
`references/deck-structure.md`.

### Step 5 — Deliver

- Save the dated `.pptx` to `output/` and surface it to the user.
- Optional: email draft (connected mail MCP) or a Canva version (Canva MCP).
- **Commit outputs/data to git** — the web container is ephemeral; anything
  not pushed is lost.

## House style (must preserve)

- 16:9 (13.33×7.5 in), dark financial look, 中文 primary + EN/IT accents.
- Header: `‹Section letter› · ‹nn› · ‹category›` (e.g. `A · 01 · PUN 历史`).
- Footer: `WiseGlow Italy · 资产运营 · GME PUN 深度分析 · ‹n›/‹N›`.
- Big-number "stat cards" + short annotation lines; €/MWh throughout.
- "代表性" tag on any reconstructed (non-official) intraday/15-min curve.

## Output language

Default **中文-primary** (per house decks), EN/IT for technical terms and
zone names. Override on request ("英文版", "in italiano").

## Weekly automation

The container is ephemeral and cannot hold a cron timer. To truly run weekly,
the user sets a **scheduled trigger** in Claude Code on the web that wakes a
session on a weekly cadence; that session runs this skill and pushes the
output. See https://code.claude.com/docs/en/claude-code-on-the-web. Document
the trigger setup, don't fake it with `sleep`.

## Pitfalls

- ❌ Rebuilding slides instead of cloning the template — loses the house style.
- ❌ Inventing market numbers when a source is blocked — fetch or ask; never
  fabricate. Mark any carried-over (un-refreshed) figure as `· 待刷新`.
- ❌ Inventing Project-1 / BESS internals — these are user-supplied only.
- ❌ Blending real + carried values inside one series — refresh a year only
  when the source covers all its months; otherwise leave that year on template
  data and tag it `· 待刷新`. Don't half-fill a line (e.g. Ember had only
  Jan–Apr 2025, so `PUN F0 2025` must not silently mix real + template months).
- ❌ Treating energy-charts zonal MCP as the exact PUN — PUN is the
  consumption-weighted zonal average; cross-check headline PUN with Ember/GME.
- ❌ Forgetting to commit/push outputs before the container is reclaimed.
- ❌ Weekly granularity vs monthly charts: a weekly run refreshes the current
  month's running average + the past week's daily PUN, it does not invent a
  new monthly point mid-month.

## File layout

```
italy-power-market-analysis/
├── SKILL.md                      ← this file (index)
├── references/
│   ├── data-sources.md           ← endpoints, tokens, allowlist, fetch recipes
│   └── deck-structure.md         ← slide-by-slide map: section, chart, data
├── scripts/
│   ├── fetch_market_data.py      ← source-ladder fetcher → market_data.json
│   ├── metrics.py                ← F1/F2/F3, zones, spreads, capture, arbitrage
│   └── build_deck.py             ← clone template, replace data, save dated pptx
└── data/
    ├── template_wiseglow.pptx    ← house template (style source of truth)
    ├── ember_italy_monthly_pun.csv ← real historical PUN (backfill/cross-check)
    ├── internal_inputs.yaml       ← Project-1 + BESS (user-supplied)
    └── market_data.json           ← assembled inputs for the deck
```
