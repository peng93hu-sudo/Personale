#!/usr/bin/env python3
"""Source-ladder fetcher: refresh market_data.json from the best available feed.

See references/data-sources.md. Under the default GitHub-only allowlist only
the Ember path works; energy-charts / ENTSO-E / GME activate once their domains
are added to the environment's network policy.

  python3 fetch_market_data.py --probe          # report reachable sources
  python3 fetch_market_data.py --refresh-pun     # update PUN F0 from Ember
  python3 fetch_market_data.py --energy-charts 2026-05-01 2026-05-23
"""
import argparse, csv, datetime as dt, json, os, re, urllib.request, urllib.error

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
MARKET = os.path.join(DATA, "market_data.json")
EMBER_CSV = os.path.join(DATA, "ember_italy_monthly_pun.csv")
EMBER_RAW = ("https://raw.githubusercontent.com/depa-tto/"
             "Multivariate-Time-Series-project-on-Electricity-Consumption-and-Prices/"
             "main/dataset/european_wholesale_electricity_price_data_monthly.csv")
EC_ZONES = {"NORD": "IT-North", "CNOR": "IT-Centre-North", "CSUD": "IT-Centre-South",
            "SUD": "IT-South", "SICI": "IT-Sicily", "SARD": "IT-Sardinia",
            "CALA": "IT-Calabria"}


def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "wiseglow-pun/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def probe():
    hosts = {"ember(github)": EMBER_RAW,
             "energy-charts": "https://api.energy-charts.info/price?bzn=IT-North"
                              "&start=2026-05-01&end=2026-05-02",
             "entsoe": "https://web-api.tp.entsoe.eu/api",
             "gme": "https://www.mercatoelettrico.org/en/"}
    for name, url in hosts.items():
        try:
            _get(url, timeout=12)
            print(f"  OK     {name}")
        except urllib.error.HTTPError as e:
            print(f"  HTTP{e.code} {name}")
        except Exception as e:
            print(f"  BLOCK  {name} ({type(e).__name__})")


def load_ember_monthly(prefer_local=True):
    """-> {'YYYY-MM': price} Italy national monthly PUN."""
    if prefer_local and os.path.exists(EMBER_CSV):
        rows = list(csv.reader(open(EMBER_CSV, encoding="utf-8")))
    else:
        text = _get(EMBER_RAW).decode("utf-8", "replace").splitlines()
        rows = list(csv.reader(text))
    out = {}
    for r in rows[1:]:
        if r[0].strip().lower() == "italy":
            out[r[2][:7]] = float(r[3])
    return out


def fetch_energy_charts(zone, start, end):
    """Hourly day-ahead for one IT zone -> [(datetime, price)]. Needs allowlist."""
    bzn = EC_ZONES[zone]
    url = f"https://api.energy-charts.info/price?bzn={bzn}&start={start}&end={end}"
    j = json.loads(_get(url))
    secs, px = j["unix_seconds"], j["price"]
    return [(dt.datetime.utcfromtimestamp(s), p) for s, p in zip(secs, px)]


def refresh_pun_f0():
    """Map Ember monthly PUN onto the deck's 'PUN F0 <year>' series in-place."""
    ember = load_ember_monthly()
    payload = json.load(open(MARKET, encoding="utf-8"))
    updated = []
    for c in payload["charts"]:
        for s in c["series"]:
            name = str(s.get("name") or "")
            if "PUN F0" in name:
                ym = re.search(r"20\d{2}", name)
                if not ym:
                    continue
                year = ym.group(0)
                newvals = [ember.get(f"{year}-{m:02d}") for m in range(1, 13)]
                if any(v is not None for v in newvals):
                    # keep existing value where Ember has no month (gaps)
                    s["values"] = [nv if nv is not None else ov
                                   for nv, ov in zip(newvals, s["values"])]
                    updated.append(f"slide{c['slide']}:{name}")
    payload.setdefault("meta", {})["pun_f0_source"] = "Ember Italy monthly"
    json.dump(payload, open(MARKET, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("refreshed:", ", ".join(updated) or "(none)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--refresh-pun", action="store_true")
    ap.add_argument("--energy-charts", nargs=2, metavar=("START", "END"))
    args = ap.parse_args()
    if args.probe:
        probe()
    if args.refresh_pun:
        refresh_pun_f0()
    if args.energy_charts:
        for z in EC_ZONES:
            try:
                hrs = fetch_energy_charts(z, *args.energy_charts)
                print(f"{z}: {len(hrs)} hourly points")
            except Exception as e:
                print(f"{z}: unavailable ({type(e).__name__}) — needs allowlist")
                break


if __name__ == "__main__":
    main()
