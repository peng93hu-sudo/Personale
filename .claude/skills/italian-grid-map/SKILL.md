---
name: italian-grid-map
description: >-
  Build and weekly-incrementally expand the Italian electrical grid interactive
  HTML map (substations, generation plants, transmission lines, HVDC) for Peng Hu
  / WiseGlow Italia. Use whenever the user says "本周做 [区域]", "继续下一周",
  "继续做地图", "更新意大利电网地图", "Mappa rete elettrica", "下一个区域", or any
  request to add/update an Italian region in the grid map. Also use when the user
  asks about Italian CP/SE/HVDC/transmission lines, the rolling 12-week regional
  plan, the pipeline regions (Lazio, Marche, Sardegna, Basilicata, Sicilia), or
  wants to (re)generate the Mappa_Rete_Elettrica HTML. Trigger even if the user
  just says "做地图" / "更新地图" without a region — load this skill and check status.
---

# Italian Grid Map — Weekly Expansion (v2 workflow)

## Purpose

Peng Hu (WiseGlow Italia — solar EPC/IPP, based in Polverigi, prov. Ancona)
maintains one interactive HTML map of the Italian electrical grid. Each week he
says one short sentence (e.g. **"本周做 Marche"** or just **"继续"**) and Claude
produces an updated **single self-contained HTML file** that adds one region's:

- **Substations 变电站**: SE 380/220 kV (RTN), SE/CP 150·132 kV (Cabine Primarie), user/RFI stations
- **Generation 发电**: solar / wind / thermal / hydro+pumped / geothermal / BESS / former-nuclear
- **Transmission 线路**: 380/220/150/132 kV AC + HVDC (operational & planned)

## Non-negotiable principles

1. **Peng is a non-coder.** Never ask him to run scripts, set up cron/CI, fetch
   data, manage packages, or do any technical setup. One sentence in → one HTML
   file out.
2. **Single self-contained HTML.** Leaflet from CDN, all data embedded as JS
   objects, all CSS inline, no asset folders, no build step.
3. **NO over-engineering.** Do **not** add GitHub Actions, generator scripts,
   "auto-index/portal" pages, or extra tooling **unless Peng explicitly asks**.
   (This was a past mistake — don't repeat it.)
4. **Verify headline data before publishing.** See "Verification" below.
5. **Bilingual.** UI section labels & messages in Chinese; place names and
   technical terms in Italian (Cabina Primaria, Stazione Elettrica). Popups mix both.
6. **Directive & concise.** Lead with the deliverable, then a compact summary
   table, then "下周 [region]". No long postambles. Ask at most ONE question, and
   only if genuinely ambiguous — otherwise just do the work.

## Environment handling (read this first)

This skill runs in different environments. **Detect and adapt:**

- **Claude Code + git repo (web / CLI / Action) — current setup:**
  - The repo is the source of truth. There is **no** `/mnt/user-data/outputs`,
    no `present_files`, no `conversation_search`. Do not call them.
  - Save the HTML **into the repo**, commit, push to the working branch, and
    keep a **draft PR** open (create one if missing — via the GitHub MCP tools).
  - Surface the file to the user with **`SendUserFile`** (the equivalent of
    `present_files`).
  - "Latest version" = the highest `Mappa_Rete_Elettrica_Italia_v{N}.html` in
    the repo. Find it with `ls`, not by searching past conversations.
- **Claude.ai app (if ever there):**
  - Save to `/mnt/user-data/outputs/Mappa_Rete_Elettrica_Italia_v{N}.html` and
    call `present_files`. "Latest version" via `conversation_search`.

Everything else (data, UI, schemas) is identical across environments.

## Master data in a single-file world

The output is one HTML, so the **embedded JS arrays in the latest HTML ARE the
master data.** To extend:

1. Read the latest `Mappa_Rete_Elettrica_Italia_v{N}.html`.
2. Copy out its `SUBSTATIONS`, `PLANTS`, `LINES` arrays.
3. **Append** the new region's entries (don't duplicate existing ones — check by
   name/coords).
4. Write the new `v{N+1}` file with the combined arrays.

(If a repo ever keeps optional `data/master_*.js`, prefer those; otherwise the
HTML is canonical.)

## 12-week regional plan & status

Baseline after **v1** (this repo): national 380/220 kV backbone + HVDC done; the
5 priority regions seeded with a starter CP set.

| Wk | Region | CP target | v1 actual | Notes |
|----|--------|-----------|-----------|-------|
| 1 | Lazio | 75 | ~10 CP | Roma + prov. |
| 2 | **Marche** | 50 | 16 CP | Peng's home — Polverigi included; densify next |
| 3 | Sardegna | 60 | 7 CP | SAPEI/SACOI terminals |
| 4 | Basilicata | 40 | 5 CP | wind uplands |
| 5 | **Sicilia** | 90 | 10 CP | **Vittoria/Ragusa project** included |
| 6 | Puglia | 110 | backbone only | large renewable cluster |
| 7 | Campania | 85 | backbone only | Napoli urban grid |
| 8 | Calabria | 60 | backbone only | SAPEI endpoint |
| 9 | Toscana | 95 | backbone only | Larderello geothermal |
| 10 | Lombardia | 200 | backbone only | heavy industry base load |
| 11 | NE+NW rest | 250 | backbone only | Veneto/Emilia/Piemonte/VdA/Liguria/FVG/TAA |
| 12 | Abruzzo+Molise+rest | 80 | backbone only | cleanup |

"继续"/"下一周" → advance to the region with the largest target-vs-actual gap
among priority regions first (so densifying the 5 pipeline regions outranks
opening a brand-new one). Named region → do that one regardless of order.

## Workflow

1. **Locate latest** `Mappa_Rete_Elettrica_Italia_v{N}.html` (`ls` the repo) and
   read its embedded data arrays.
2. **Confirm region.** "本周做 X" → X. "继续" → next per the table. Ambiguous →
   one short question (2-3 options from the roadmap).
3. **Build the regional dataset** and append to the arrays (schemas below):
   all CP (150/20 & 132/20) by province toward the target, all SE in-region,
   major plants, in-region + cross-border line segments. ~80% real-CP coverage
   using known towns / industrial zones / plant interconnections is fine.
4. **Verify** the new region's headline facilities (see Verification).
5. **Generate** the single HTML as `v{N+1}`, reusing the UI scaffold (below).
   Keep the indicative-data disclaimer.
6. **Ship:** commit + push to the working branch, ensure a draft PR exists,
   `SendUserFile` the HTML. Reply with a compact summary + "下周 [region]".

## Verification (before each publish)

The data is hand-built and **indicative** — always keep the disclaimer. But for
the **headline / largest** facilities of the region being added, spot-check with
`WebSearch` and fix errors before shipping:

- Capacity (MW) and fuel/type of the biggest plants.
- Operational **status** (e.g. Italian coal phase-out was postponed to **2038**;
  Torrevaldaliga Nord & Cerano are in "cold reserve", not running).
- "Largest/first" superlatives (e.g. Larderello = world's first geothermal, 1913;
  Entracque = Italy's largest hydro).
- Lesson: v1 had Montalto «A. Volta» wrong (it's an ex-multifuel plant largely
  dismessa, ~960 MW today, not a 3300 MW CCGT). Don't trust round numbers.

Cite sources in the chat summary. Coordinates stay approximate (note it).

## Sharing (only if asked)

For a shareable URL, **GitHub Pages** is the route (one-time user setting:
Settings → Pages). Keep versioned filenames for history; optionally refresh a
small `index.html` that redirects to the latest version so the public URL stays
stable. Do NOT enable Pages or merge PRs without the user's say-so.

## Data schemas (match v1 exactly so versions stay consistent)

```js
// cat = "sub"
SUBSTATIONS: { n, t, kv, region, prov, lat, lng, note? }
//   t ∈ "SE380" | "SE220" | "CP"
// cat = "plant"
PLANTS:      { n, t, mw, region, lat, lng, note? }
//   t ∈ "solar" | "wind" | "thermal" | "hydro" | "geo" | "bess" | "nuclear_x"
// cat = "line"
LINES:       { n, t, kv, c:[[lat,lng],...], note? }
//   t ∈ "ac380" | "ac220" | "hvdc" | "hvdc_plan"
```

Type colours / labels (keep stable): SE380 #ff5252, SE220 #ffab40, CP #ffd740;
solar #ffee58, wind #69f0ae, thermal #ff8a65, hydro #40c4ff, geo #b388ff,
bess #ff80ab, nuclear_x #b0bec5 (default OFF — dismesse); ac380 #ff5252,
ac220 #ffab40, hvdc #00e5ff, hvdc_plan #00e5ff dashed.

`REGION_BOUNDS[region] = [[south,west],[north,east]]` for the region filter/zoom.

## UI scaffold (keep across versions)

- Leaflet 1.9.4 (unpkg CDN) + CartoDB Dark Matter tiles, dark theme.
- 3 tabs: **变电站 / 发电 / 线路**, each with master + per-sublayer toggles + counts.
- Region `<select>` (filter + fitBounds), name search box, stat cards, legend.
- Custom panes so markers sit above lines; circleMarkers sized by MW; polylines
  styled by kV/type. Mobile-responsive. Indicative-data disclaimer in the footer.
- After writing, sanity-check: `node --check` the inline script and run it once
  against DOM/Leaflet stubs to catch init errors.

## Peng context

- Polverigi (prov. Ancona, Marche) — local Marche detail valued.
- Active project: **Vittoria, prov. Ragusa, Sicilia — solar 4.86 MWp** — extra
  detail when doing Sicilia.
- 5 operational-priority regions: Lazio, Marche, Sardegna, Basilicata, Sicilia.
- Bilingual IT/ZH; structured deliverables (HTML/Excel); concise, directive style.

## When in doubt

- Default to **doing the work**; ask ≤1 question only if truly ambiguous.
- Never propose scripts / CI / cron / manual technical setup.
- Keep it a single self-contained HTML.
- Verify headline data before publishing; keep the indicative-data disclaimer.
