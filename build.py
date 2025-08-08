#!/usr/bin/env python3
"""
Climate Now → 2050 — auto-building static dashboard
- Pulls: NOAA CO₂ (monthly), NSIDC Arctic Sea Ice (daily), Met Éireann warnings (JSON),
         PSMSL Dublin link, NOAA NCEI Ocean Heat Content (0–2000 m, best-effort)
- Renders: dist/index.html (+ optional PNG charts)
"""

from __future__ import annotations
import sys
import io
import re
import csv
import json
import math
import gzip
import traceback
from pathlib import Path
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")  # headless-safe for local/CI
import matplotlib.pyplot as plt
import requests
import pandas as pd
import numpy as np

OUT = Path("dist")
OUT.mkdir(parents=True, exist_ok=True)

# ---------- Helpers ----------
def http_get(url: str, timeout=30, allow_redirects=True) -> requests.Response:
    r = requests.get(
        url,
        timeout=timeout,
        allow_redirects=allow_redirects,
        headers={"User-Agent": "climate-dashboard/1.1 (+github actions)"},
    )
    r.raise_for_status()
    return r

def try_urls(urls, timeout=45, binary=False):
    """Try a list of URLs and return (url, text_or_bytes)."""
    last_err = None
    for u in urls:
        try:
            r = http_get(u, timeout=timeout)
            return u, (r.content if binary else r.text)
        except Exception as e:
            last_err = e
            continue
    raise last_err if last_err else RuntimeError("No URLs tried")

def save_png(fig, path: Path, dpi=160):
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

def now_utc_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def fmt(val, default="—", ndigits=2):
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return default
        if isinstance(val, (int, np.integer)):
            return f"{val}"
        if isinstance(val, (float, np.floating)):
            return f"{val:.{ndigits}f}"
        return str(val)
    except Exception:
        return default

# ---------- Data fetchers ----------
def fetch_noaa_co2_monthly():
    """
    NOAA GML Mauna Loa CO₂ monthly CSV:
    https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv
    """
    url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"
    r = http_get(url)
    lines = [ln for ln in r.text.splitlines() if ln.strip() and not ln.startswith("#")]
    df = pd.read_csv(io.StringIO("\n".join(lines)), header=None)

    # columns (as of 2025): year, month, decimal_date, average, deseasonalized, num_days, stdev, uncertainty, ...
    cols = ["year", "month", "decimal_date", "average", "deseasonalized", "num_days", "stdev", "uncertainty"]
    if df.shape[1] > len(cols):
        cols += list(range(len(cols), df.shape[1]))
    df.columns = cols

    df = df.replace(-99.99, np.nan).dropna(subset=["average"])
    latest = df.iloc[-1]
    latest_ppm = float(latest["average"])
    latest_year = int(latest["year"])
    latest_month = int(latest["month"])

    # Chart: last 24 months
    tail = df.tail(24).copy()
    dates = pd.to_datetime(
        tail["year"].astype(int).astype(str) + "-" + tail["month"].astype(int).astype(str) + "-15",
        errors="coerce",
    )
    fig = plt.figure()
    plt.plot(dates, tail["average"], marker="o")
    plt.title("Mauna Loa CO₂ (last 24 months)")
    plt.ylabel("ppm")
    plt.xlabel("")
    plt.grid(True, alpha=0.3)
    save_png(fig, OUT / "co2_24mo.png")

    return {
        "year": latest_year,
        "month": latest_month,
        "ppm": latest_ppm,
        "chart": "co2_24mo.png",
        "source": "https://gml.noaa.gov/ccgg/trends/",
    }

def fetch_met_eireann_warnings():
    """
    Official JSON:
    https://www.met.ie/Open_Data/json/warning_IRELAND.json
    """
    url = "https://www.met.ie/Open_Data/json/warning_IRELAND.json"
    try:
        data = http_get(url, timeout=30).json()
        items = data.get("warnings", []) or []
        active = [w for w in items if (w.get("status", "") or "").lower() == "active"]
        titles = [w.get("title") for w in active if w.get("title")] or []
        return {
            "count": len(active),
            "titles": titles[:3],
            "source": "https://www.met.ie/warnings",
        }
    except Exception:
        return {"count": "N/A", "titles": [], "source": "https://www.met.ie/warnings"}

def fetch_psmsl_dublin_note():
    # Keep simple; PSMSL page for Dublin (Station 432)
    return {
        "link": "https://psmsl.org/data/obtaining/stations/432.php",
        "note": "See PSMSL Station 432 (Dublin) for latest tide-gauge trend.",
    }

def _parse_nsidc_daily_csv(text: str):
    """Parse NSIDC daily CSV that includes comment lines + header row."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    # Find header row (starts with 'year' or 'yyyy')
    start_idx = 0
    for i, ln in enumerate(lines):
        if ln.lower().startswith("year") or ln.lower().startswith("yyyy"):
            start_idx = i
            break
    csv_text = "\n".join(lines[start_idx:])
    df = pd.read_csv(io.StringIO(csv_text))
    # columns vary; find by heuristics
    ycol = next((c for c in df.columns if c.lower().startswith("y")), None)
    mcol = next((c for c in df.columns if c.lower().startswith("m")), None)
    dcol = next((c for c in df.columns if c.lower().startswith("d")), None)
    ecol = next((c for c in df.columns if "extent" in c.lower()), None)
    if not all([ycol, mcol, dcol, ecol]):
        raise ValueError("Unexpected NSIDC CSV columns")

    df["date"] = pd.to_datetime(
        df[ycol].astype(int).astype(str)
        + "-"
        + df[mcol].astype(int).astype(str)
        + "-"
        + df[dcol].astype(int).astype(str),
        errors="coerce",
    )
    df = df.dropna(subset=["date"]).sort_values("date")
    df = df.replace(-9999, np.nan)
    return df, ecol

def fetch_nsidc_arctic_daily():
    """
    NSIDC Sea Ice Index v3 — Arctic daily extent.
    Try multiple mirrors and .csv.gz fallback.
    """
    candidates_text = [
        # Primary
        "https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv",
        # Same path but gz (sometimes present)
        "https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv.gz",
        # Historic mirror
        "https://sidads.colorado.edu/DATASETS/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv",
        "https://sidads.colorado.edu/DATASETS/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv.gz",
    ]

    # Try to get plain text first, then gz
    for url in candidates_text:
        try:
            if url.endswith(".gz"):
                u, content = try_urls([url], binary=True)
                text = gzip.decompress(content).decode("utf-8", "replace")
            else:
                u, text = try_urls([url], binary=False)
            df, ecol = _parse_nsidc_daily_csv(text)
            latest_row = df.dropna(subset=[ecol]).iloc[-1]
            latest_val = float(latest_row[ecol])  # million km²
            latest_date = str(latest_row["date"].date())

            # Sparkline last 365 days (if available)
            tail = df.dropna(subset=[ecol]).tail(365).copy()
            fig = plt.figure()
            plt.plot(tail["date"], tail[ecol])
            plt.title("Arctic Sea Ice Extent (last 365 days)")
            plt.ylabel("million km²")
            plt.xlabel("")
            plt.grid(True, alpha=0.3)
            save_png(fig, OUT / "arctic_extent_365d.png")

            return {
                "latest": {"date": latest_date, "extent_mkm2": latest_val},
                "chart": "arctic_extent_365d.png",
                "source": "https://nsidc.org/sea-ice-today",
            }
        except Exception:
            continue

    # If every URL failed, degrade gracefully
    return {
        "latest": {"date": "N/A", "extent_mkm2": float("nan")},
        "chart": "",
        "source": "https://nsidc.org/sea-ice-today",
    }

def fetch_noaa_ncei_ohc_latest():
    """
    NOAA NCEI Global Ocean Heat Content (0–2000 m) — try a few endpoints.
    If all fail, return placeholder.
    """
    candidates = [
        "https://www.ncei.noaa.gov/data/ocean-heat-content/anomaly/ohc_levitus_climdash/ohc_0-2000m_annual.csv",
        "https://www.ncei.noaa.gov/data/ocean-heat-content/anomaly/ohc_levitus_climdash/ohc_0-2000m_annual_mean.csv",
        "https://www.ncei.noaa.gov/access/global-ocean-heat-content/ohc_0-2000m.csv",
    ]
    for url in candidates:
        try:
            text = try_urls([url], timeout=45, binary=False)[1]
            lines = [ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
            df = pd.read_csv(io.StringIO("\n".join(lines)))
            # choose year column and first numeric column
            year_col = next((c for c in df.columns if str(c).lower().startswith("year")), None)
            if year_col is None:
                year_col = "Year" if "Year" in df.columns else df.columns[0]
            num_cols = [c for c in df.columns if c != year_col and pd.api.types.is_numeric_dtype(df[c])]
            if not num_cols:
                continue
            df = df.dropna(subset=num_cols).sort_values(year_col)
            last = df.iloc[-1]
            latest_year = int(last[year_col])
            latest_val = float(last[num_cols[0]])
            units = "J × 10^22"  # typical for OHC series (adjust if needed)
            return {"year": latest_year, "value": latest_val, "units": units,
                    "source": "https://www.ncei.noaa.gov/access/global-ocean-heat-content/"}
        except Exception:
            continue

    return {"year": "N/A", "value": "N/A", "units": "", "source": "https://www.ncei.noaa.gov/access/global-ocean-heat-content/"}

# ---------- HTML ----------
def build_html(ctx: dict) -> str:
    now = now_utc_str()
    co2 = ctx["co2"]
    warn = ctx["warnings"]
    dublin = ctx["dublin"]
    nsidc = ctx["nsidc"]
    ohc = ctx["ohc"]

    def tile(label, value, sub=""):
        return f"""
        <div class="card">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
          <div class="sub">{sub}</div>
        </div>
        """.strip()

    co2_sub = f'Latest: {co2.get("year","N/A")}-{str(co2.get("month","")).zfill(2)} · <b>Source</b>: <a href="{co2["source"]}">NOAA GML</a>'
    warn_titles = ", ".join(warn.get("titles") or []) if isinstance(warn.get("titles"), list) else "—"
    warn_sub = f'{warn_titles or "—"} · <b>Source</b>: <a href="{warn["source"]}">Met Éireann</a>'
    dublin_sub = f'<b>Source</b>: <a href="{dublin["link"]}">PSMSL Station 432</a>'
    nsidc_latest = nsidc.get("latest", {})
    nsidc_val = nsidc_latest.get("extent_mkm2", float("nan"))
    nsidc_date = nsidc_latest.get("date", "N/A")
    nsidc_sub = f'Latest: {nsidc_date} · <b>Source</b>: <a href="{nsidc["source"]}">NSIDC Sea Ice Today</a>'
    ohc_sub = f'Latest year: {ohc.get("year","N/A")} · <b>Source</b>: <a href="{ohc["source"]}">NOAA NCEI</a>'

    nsidc_chart_html = (
        f'<img src="{nsidc["chart"]}" alt="Arctic sea-ice extent sparkline">'
        if nsidc.get("chart")
        else "<div class='sub'>Chart unavailable this run.</div>"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Climate Now & to 2050 — Dashboard</title>
<style>
  body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; margin: 20px; }}
  .header {{ display:flex; align-items:baseline; justify-content:space-between; flex-wrap:wrap; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-top: 16px; }}
  .card {{ border:1px solid #ddd; border-radius:12px; padding:16px; }}
  .label {{ font-size: 12px; text-transform: uppercase; letter-spacing: .08em; opacity: .75; }}
  .value {{ font-size: 26px; font-weight: 700; margin-top: 6px; }}
  .sub {{ font-size: 13px; opacity: .85; margin-top: 6px; }}
  .foot {{ font-size: 12px; opacity: .8; margin-top: 24px; }}
  img {{ width: 100%; height: auto; border:1px solid #eee; border-radius: 8px; }}
  a {{ color: inherit; }}
</style>
</head>
<body>
  <div class="header">
    <h1>Climate Now & to 2050 — Dashboard</h1>
    <div class="sub">Generated: {now}</div>
  </div>

  <div class="grid">
    {tile("Atmospheric CO₂ (Mauna Loa, monthly)", f'{fmt(co2.get("ppm"))} ppm', co2_sub)}
    {tile("Met Éireann Warnings (Ireland)", f'{fmt(warn.get("count"))} active', warn_sub)}
    {tile("Dublin Tide Gauge", dublin["note"], dublin_sub)}
    {tile("Arctic Sea Ice Extent", f'{fmt(nsidc_val)} million km²', nsidc_sub)}
    {tile("Ocean Heat Content (0–2000 m)", f'{fmt(ohc.get("value"))} {ohc.get("units","")}', ohc_sub)}
  </div>

  <div class="grid" style="margin-top:24px">
    <div class="card">
      <div class="label">Mauna Loa CO₂ (last 24 months)</div>
      <img src="{co2.get("chart","")}" alt="CO₂ last 24 months">
    </div>
    <div class="card">
      <div class="label">Arctic Sea Ice (last 365 days)</div>
      {nsidc_chart_html}
    </div>
  </div>

  <div class="foot">
    <p>This page is rebuilt on schedule (or on demand). If a data source is temporarily unreachable,
    the dashboard will still build and show placeholders.</p>
  </div>
</body>
</html>
"""
    return html

# ---------- Main ----------
def main():
    try:
        co2 = fetch_noaa_co2_monthly()
    except Exception:
        traceback.print_exc()
        co2 = {"year": "N/A", "month": 0, "ppm": float("nan"), "chart": "", "source": "https://gml.noaa.gov/ccgg/trends/"}

    try:
        warnings = fetch_met_eireann_warnings()
    except Exception:
        traceback.print_exc()
        warnings = {"count": "N/A", "titles": [], "source": "https://www.met.ie/warnings"}

    dublin = fetch_psmsl_dublin_note()

    try:
        nsidc = fetch_nsidc_arctic_daily()
    except Exception:
        traceback.print_exc()
        nsidc = {"latest": {"date": "N/A", "extent_mkm2": float("nan")}, "chart": "", "source": "https://nsidc.org/sea-ice-today"}

    try:
        ohc = fetch_noaa_ncei_ohc_latest()
    except Exception:
        traceback.print_exc()
        ohc = {"year": "N/A", "value": "N/A", "units": "", "source": "https://www.ncei.noaa.gov/access/global-ocean-heat-content/"}

    ctx = {"co2": co2, "warnings": warnings, "dublin": dublin, "nsidc": nsidc, "ohc": ohc}
    html = build_html(ctx)
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("Wrote", OUT / "index.html")

if __name__ == "__main__":
    main()
