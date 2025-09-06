#!/usr/bin/env python3
"""
Data fetching functions for the Climate Dashboard.

This module contains all functions responsible for fetching climate data
from various sources like NOAA, NSIDC, Met Éireann, etc.
"""

from __future__ import annotations
import io
import gzip
import traceback
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from utils import http_get, try_urls, fmt_num, m_to_inches


# Output directory for generated files
OUT = Path("dist")
OUT.mkdir(parents=True, exist_ok=True)


def save_png(fig, path: Path, dpi: int = 160) -> None:
    """
    Save a matplotlib figure as PNG with proper formatting.
    
    Args:
        fig: Matplotlib figure object
        path: Output file path
        dpi: Resolution for the saved image
    """
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def fetch_noaa_co2_monthly() -> dict:
    """
    Fetch monthly CO₂ data from NOAA's Mauna Loa observatory.
    
    Returns:
        Dictionary containing CO₂ data and chart information
    """
    url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"
    r = http_get(url)
    lines = [ln for ln in r.text.splitlines() if ln.strip() and not ln.startswith("#")]
    df = pd.read_csv(io.StringIO("\n".join(lines)), header=None)
    
    # Set up column names
    cols = ["year","month","decimal_date","average","deseasonalized","num_days","stdev","uncertainty"]
    if df.shape[1] > len(cols): 
        cols += list(range(len(cols), df.shape[1]))
    df.columns = cols
    
    # Clean data and get latest values
    df = df.replace(-99.99, np.nan).dropna(subset=["average"])
    latest = df.iloc[-1]
    latest_ppm = float(latest["average"])
    latest_year = int(latest["year"])
    latest_month = int(latest["month"])

    # Create 24-month trend chart
    tail = df.tail(24).copy()
    dates = pd.to_datetime(
        tail["year"].astype(int).astype(str) + "-" + tail["month"].astype(int).astype(str) + "-15",
        errors="coerce",
    )
    fig = plt.figure(figsize=(10, 6))
    plt.plot(dates, tail["average"], marker="o", linewidth=2, markersize=4)
    plt.title("Mauna Loa CO₂ (last 24 months)", fontsize=14, fontweight='bold')
    plt.ylabel("ppm", fontsize=12)
    plt.xlabel("")
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    # Format y-axis to show integers
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
    save_png(fig, OUT / "co2_24mo.png")

    return {
        "year": latest_year, 
        "month": latest_month, 
        "ppm": latest_ppm,
        "chart": "co2_24mo.png", 
        "source": "https://gml.noaa.gov/ccgg/trends/"
    }


def fetch_met_eireann_warnings() -> dict:
    """
    Fetch active weather warnings from Met Éireann (Ireland).
    
    Returns:
        Dictionary containing warning count and titles
    """
    url = "https://www.met.ie/Open_Data/json/warning_IRELAND.json"
    try:
        data = http_get(url, timeout=30).json()
        items = data.get("warnings", []) or []
        active = [w for w in items if (w.get("status","") or "").lower() == "active"]
        titles = [w.get("title") for w in active if w.get("title")] or []
        return {
            "count": len(active), 
            "titles": titles[:3], 
            "source": "https://www.met.ie/warnings"
        }
    except Exception:
        return {
            "count": "N/A", 
            "titles": [], 
            "source": "https://www.met.ie/warnings"
        }


def fetch_psmsl_dublin_note() -> dict:
    """
    Get information about Dublin tide gauge data.
    
    Returns:
        Dictionary with Dublin tide gauge information
    """
    return {
        "link": "https://psmsl.org/data/obtaining/stations/432.php",
        "note": "Dublin tide-gauge shows a gradual long-term rise."
    }


def _parse_nsidc_daily_csv(text: str) -> tuple[pd.DataFrame, str]:
    """
    Parse NSIDC daily sea ice extent CSV data.
    
    Args:
        text: Raw CSV text from NSIDC
        
    Returns:
        Tuple of (dataframe, extent_column_name)
    """
    lines = [ln for ln in text.splitlines() if ln.strip()]
    start_idx = 0
    
    # Find header row
    for i, ln in enumerate(lines):
        if ln.lower().startswith("year") or ln.lower().startswith("yyyy"):
            start_idx = i
            break
    
    csv_text = "\n".join(lines[start_idx:])
    df = pd.read_csv(io.StringIO(csv_text))
    
    # Find relevant columns
    ycol = next((c for c in df.columns if c.lower().startswith("y")), None)
    mcol = next((c for c in df.columns if c.lower().startswith("m")), None)
    dcol = next((c for c in df.columns if c.lower().startswith("d")), None)
    ecol = next((c for c in df.columns if "extent" in c.lower()), None)
    
    if not all([ycol, mcol, dcol, ecol]): 
        raise ValueError("Unexpected NSIDC CSV columns")
    
    # Create date column and clean data
    df["date"] = pd.to_datetime(
        df[ycol].astype(int).astype(str) + "-" + 
        df[mcol].astype(int).astype(str) + "-" + 
        df[dcol].astype(int).astype(str),
        errors="coerce"
    )
    df = df.dropna(subset=["date"]).sort_values("date")
    df = df.replace(-9999, np.nan)
    
    return df, ecol


def fetch_nsidc_arctic_daily() -> dict:
    """
    Fetch Arctic sea ice extent data from NSIDC.
    
    Returns:
        Dictionary containing sea ice data and chart information
    """
    candidates = [
        "https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv",
        "https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv.gz",
        "https://sidads.colorado.edu/DATASETS/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv",
        "https://sidads.colorado.edu/DATASETS/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv.gz",
    ]
    
    for url in candidates:
        try:
            if url.endswith(".gz"):
                _, content = try_urls([url], binary=True)
                text = gzip.decompress(content).decode("utf-8", "replace")
            else:
                _, text = try_urls([url], binary=False)
            
            df, ecol = _parse_nsidc_daily_csv(text)
            latest_row = df.dropna(subset=[ecol]).iloc[-1]
            latest_val = float(latest_row[ecol])
            latest_date = str(latest_row["date"].date())
            
            # Create 365-day trend chart
            tail = df.dropna(subset=[ecol]).tail(365).copy()
            fig = plt.figure(figsize=(12, 6))
            plt.plot(tail["date"], tail[ecol], linewidth=2, color='#2E86AB')
            plt.title("Arctic Sea Ice Extent (last 365 days)", fontsize=14, fontweight='bold')
            plt.ylabel("million km²", fontsize=12)
            plt.xlabel("")
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            # Format y-axis to show integers
            ax = plt.gca()
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
            save_png(fig, OUT / "arctic_extent_365d.png")
            
            return {
                "latest": {"date": latest_date, "extent_mkm2": latest_val},
                "chart": "arctic_extent_365d.png",
                "source": "https://nsidc.org/sea-ice-today"
            }
        except Exception:
            continue
    
    return {
        "latest": {"date": "N/A", "extent_mkm2": float("nan")},
        "chart": "",
        "source": "https://nsidc.org/sea-ice-today"
    }


def fetch_forest_fires_data() -> dict:
    """
    Fetch forest fires data from NASA FIRMS (Fire Information for Resource Management System).
    
    Returns:
        Dictionary containing forest fires data and information
    """
    try:
        # NASA FIRMS API for active fires (last 24 hours)
        url = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/3b46de7c8b5a4154a05a87c549d73836/VIIRS_SNPP_NRT/world/1"
        r = http_get(url, timeout=30)
        
        # Parse CSV data
        lines = r.text.strip().split('\n')
        if len(lines) > 1:  # Has data beyond header
            fire_count = len(lines) - 1  # Subtract header row
        else:
            fire_count = 0
            
        return {
            "count": fire_count,
            "source": "https://firms.modaps.eosdis.nasa.gov/",
            "description": "Active fires detected by VIIRS satellite in last 24 hours"
        }
    except Exception:
        return {
            "count": "N/A",
            "source": "https://firms.modaps.eosdis.nasa.gov/",
            "description": "Fire data temporarily unavailable"
        }


def fetch_noaa_ncei_ohc_latest() -> dict:
    """
    Fetch latest ocean heat content data from NOAA NCEI.
    
    Returns:
        Dictionary containing ocean heat content data
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
            
            year_col = next((c for c in df.columns if str(c).lower().startswith("year")), df.columns[0])
            num_cols = [c for c in df.columns if c != year_col and pd.api.types.is_numeric_dtype(df[c])]
            if not num_cols: 
                continue
            
            df = df.dropna(subset=num_cols).sort_values(year_col)
            last = df.iloc[-1]
            latest_year = int(last[year_col])
            latest_val = float(last[num_cols[0]])
            
            return {
                "year": latest_year, 
                "value": latest_val, 
                "units": "J × 10^22",
                "source": "https://www.ncei.noaa.gov/access/global-ocean-heat-content/"
            }
        except Exception:
            continue
    
    return {
        "year": "N/A",
        "value": "N/A", 
        "units": "",
        "source": "https://www.ncei.noaa.gov/access/global-ocean-heat-content/"
    }
