# Data Sources — Italy Power Market

How to obtain the inputs the deck needs, ranked by ease, with the exact
network reality of Claude Code on the web.

## Network allowlist reality (verified)

Claude Code on the web runs behind an allowlist proxy chosen at environment
creation. Probed behaviour:

| Reachable (200/301) | Blocked (403) |
|---|---|
| `pypi.org`, `files.pythonhosted.org` | `mercatoelettrico.org`, `gme.mercatoelettrico.org` |
| `github.com`, `raw.githubusercontent.com` | `web-api.tp.entsoe.eu`, `transparency.entsoe.eu` |
| `codeload.github.com`, `objects.githubusercontent.com` | `api.energy-charts.info`, `energy-charts.info` |
| | `www.terna.it`, and the open internet generally |

**Implication:** under the default GitHub-only policy, only the **Ember-via-GitHub**
path (below) works. To use energy-charts / ENTSO-E / GME you must add their
domains to the environment's network allowlist (likely requires creating a new
environment with a broader/custom policy). Docs:
https://code.claude.com/docs/en/claude-code-on-the-web

## Source ladder

### 1. energy-charts.info  — recommended engine (no token)

Fraunhofer ISE public API. Hourly day-ahead price per Italian bidding zone.

- Allowlist: `api.energy-charts.info`
- Endpoint: `GET https://api.energy-charts.info/price?bzn={ZONE}&start={YYYY-MM-DD}&end={YYYY-MM-DD}`
- IT zone `bzn` codes: `IT-North`, `IT-Centre-North`, `IT-Centre-South`,
  `IT-South`, `IT-Sicily`, `IT-Sardinia`, `IT-Calabria`
- Returns `{ unix_seconds[], price[] }` (EUR/MWh). Derive F1/F2/F3, monthly
  means, intraday, and zone spreads from the hourly series.

### 2. ENTSO-E Transparency  — authoritative zonal (free token)

- Allowlist: `web-api.tp.entsoe.eu` (+ `transparency.entsoe.eu` for signup)
- Token: register at `transparency.entsoe.eu`, then email
  `transparency@entsoe.eu` requesting "API access"; token arrives by email.
- Day-ahead prices = document type **A44**, one call per bidding-zone domain:
  `GET /api?securityToken=…&documentType=A44&in_Domain={EIC}&out_Domain={EIC}&periodStart=YYYYMMDDHHMM&periodEnd=YYYYMMDDHHMM`
- IT bidding-zone EIC codes:
  - NORD `10Y1001A1001A73I` · CNOR `10Y1001A1001A70O` ·
    CSUD `10Y1001A1001A71M` · SUD `10Y1001A1001A788` ·
    CALA `10Y1001C--00096J` · SICI `10Y1001A1001A75E` · SARD `10Y1001A1001A74G`
- Use the `entsoe-py` PyPI package (`pip install entsoe-py`) to avoid hand-XML.

### 3. GME official  — canonical PUN (terms-cookie or FTP creds)

The authoritative PUN/zonal source; matches the reference deck exactly.

- Allowlist: `www.mercatoelettrico.org`, `gme.mercatoelettrico.org`
- **Website download:** the MGP results download requires accepting the terms
  of use first (sets a session cookie), then daily/period XML/ZIP of
  `MGP_Prezzi`. Automate by POSTing the "accept" form, carrying the cookie,
  then fetching the download URL.
- **FTP (operators):** connect to the GME FTP host with operator credentials,
  then `cd MercatiElettrici/MGP_Prezzi/` and `RETR` the daily XML files.
  (Mechanism confirmed from the open-source `kiloVolt91/mercato_elettrico`
  datalogger; host + credentials are issued by GME on registration.)
- XML parsing: each file holds hourly per-zone prices + PUN; parse `<Prezzo>`
  rows, comma decimal separator → float.

### 4. Ember monthly via GitHub  — works under default allowlist

National **monthly** PUN (= Italy wholesale), historical, for backfill /
sanity check. This is the only real source reachable with no allowlist change.

- Dataset: Ember "European wholesale electricity prices" (CC-BY).
- Reachable copy used to seed `data/ember_italy_monthly_pun.csv`.
- Columns: `Country, ISO3 Code, Date, Price (EUR/MWhe)`; filter `Country=Italy`.
- Coverage observed: 2015-01 → 2025-04 (snapshot; not auto-updated).
- Cross-check: 2024 monthly = 99.14 / 87.6 / 88.85 / 86.76 / 94.94 / 103.18 /
  112.38 / 128.51 / 117.08 / 116.72 / 130.93 / 135.04 — matches the deck's
  `PUN F0 2024` series, confirming PUN F0 == this series.

## Internal inputs (user-supplied — never fetch/invent)

Keep in `data/internal_inputs.yaml`:

```yaml
project1:
  zone: CNOR            # 中北 / Marche
  annual_generation_mwh: 2966
  monthly:              # GSE settlement: month -> {gen_mwh, revenue_eur, price}
    2025-05: { price: 67.6 }
    # …11 months
portfolio:              # 5-project → zone map for the BESS-by-zone slide
  - { name: 项目1,        region: Marche,     zone: CNOR }
  - { name: WG Lazio,      region: Lazio,      zone: CSUD }
  - { name: WG Basilicata, region: Basilicata, zone: SUD  }
  - { name: WG Sicilia,    region: Sicilia,    zone: SICI }
  - { name: WG Sardegna,   region: Sardegna,   zone: SARD }
bess:
  capex_eur_per_mwh: 375000
  round_trip_eff: 0.88
  cycles_per_year: 180
  macse_eur, msd_eur: …    # capacity + ancillary revenue assumptions
```

## Freshness note

- energy-charts / ENTSO-E / GME: daily, suitable for true weekly refresh.
- Ember-via-GitHub: monthly snapshot, lags — backfill only, not a weekly feed.
- A weekly run updates the **current month's running average** and the **past
  week's daily PUN**; it does not fabricate a finished monthly data point.
