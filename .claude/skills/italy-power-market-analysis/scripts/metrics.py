#!/usr/bin/env python3
"""Derived market metrics from hourly zonal prices.

Pure functions (no I/O) so they're easy to test. Feed them hourly day-ahead
prices (from energy-charts / ENTSO-E / GME) and they produce the series the
deck shows: F1/F2/F3 bands, monthly means, spreads, capture rate, arbitrage.
"""
from __future__ import annotations
import datetime as dt
from statistics import mean

ZONES = ["NORD", "CNOR", "CSUD", "SUD", "CALA", "SICI", "SARD"]


def classify_band(ts: dt.datetime, holidays: set[dt.date] | None = None) -> str:
    """Italian fasce orarie (ARERA). F1 day-peak, F2 evening/shoulder, F3 valley."""
    holidays = holidays or set()
    wd, h = ts.weekday(), ts.hour          # Mon=0 .. Sun=6
    if ts.date() in holidays or wd == 6:    # holidays + Sundays -> F3
        return "F3"
    if wd <= 4:                              # Mon-Fri
        if 8 <= h < 19:
            return "F1"
        if h == 7 or 19 <= h < 23:
            return "F2"
        return "F3"
    if wd == 5:                              # Sat
        return "F2" if 7 <= h < 23 else "F3"
    return "F3"


def aggregate_bands(hourly, holidays=None):
    """hourly: iterable of (datetime, price). -> {'F0','F1','F2','F3': mean}."""
    buckets = {"F1": [], "F2": [], "F3": []}
    allp = []
    for ts, p in hourly:
        if p is None:
            continue
        buckets[classify_band(ts, holidays)].append(p)
        allp.append(p)
    out = {b: (round(mean(v), 2) if v else None) for b, v in buckets.items()}
    out["F0"] = round(mean(allp), 2) if allp else None
    return out


def monthly_mean(hourly):
    """-> {'YYYY-MM': mean_price} over the hourly series."""
    by = {}
    for ts, p in hourly:
        if p is None:
            continue
        by.setdefault(f"{ts.year:04d}-{ts.month:02d}", []).append(p)
    return {k: round(mean(v), 2) for k, v in sorted(by.items())}


def cross_zone_spread(zone_month: dict[str, dict[str, float]]):
    """zone_month: {zone: {'YYYY-MM': price}} -> {'YYYY-MM': max-min}."""
    months = sorted({m for d in zone_month.values() for m in d})
    out = {}
    for m in months:
        vals = [d[m] for d in zone_month.values() if m in d and d[m] is not None]
        if vals:
            out[m] = round(max(vals) - min(vals), 2)
    return out


def capture_rate(realised_price: float, zone_baseload: float) -> float:
    """Project realised €/MWh vs zone baseload, as %."""
    return round(100.0 * realised_price / zone_baseload, 1) if zone_baseload else None


def single_cycle_arbitrage(charge_eur, discharge_eur, mwh, round_trip_eff=0.88,
                           cycles_per_year=180):
    """Gross arbitrage economics for a BESS doing one cycle/day."""
    per_cycle = (discharge_eur - charge_eur) * mwh * round_trip_eff
    return {
        "spread_eur_mwh": round(discharge_eur - charge_eur, 1),
        "eur_per_cycle": round(per_cycle, 0),
        "eur_per_year": round(per_cycle * cycles_per_year, 0),
    }


def year_stats(monthly_values):
    """List of 12 monthly values -> mean/max/min/range/std/cv for the A-section."""
    v = [x for x in monthly_values if x is not None]
    if not v:
        return None
    m = mean(v)
    var = mean((x - m) ** 2 for x in v)
    sd = var ** 0.5
    return {"mean": round(m, 1), "max": round(max(v), 1), "min": round(min(v), 1),
            "range": round(max(v) - min(v), 1), "std": round(sd, 1),
            "cv_pct": round(100 * sd / m, 1) if m else None}


if __name__ == "__main__":          # tiny self-test
    import calendar
    # one synthetic week of flat 100 -> F0 == 100
    base = dt.datetime(2026, 5, 18)  # a Monday
    hrs = [(base + dt.timedelta(hours=i), 100.0) for i in range(24 * 7)]
    print("bands:", aggregate_bands(hrs))
    print("year_stats:", year_stats([99.16, 87.6, 88.86, 86.8, 94.94, 103.18,
                                      112.38, 128.51, 117.08, 116.72, 130.93, 135.04]))
