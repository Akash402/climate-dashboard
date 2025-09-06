#!/usr/bin/env python3
"""
Climate Now → 2050 — static dashboard (friendly UI)

This is the main entry point for the climate dashboard generator.
It orchestrates data fetching and HTML generation to create a static
dashboard with real-time climate data.

Features:
- Simple/Details views
- Count-up animations, reveal-on-scroll
- Scenario toggle (Low/Mid/High) + year slider for sea-level projection
- Plain-language explanations + friendly units
- Robust fetchers with graceful fallback
- Google AdSense integration

Run:
  pip install -r requirements.txt
  python build.py
"""

from __future__ import annotations
import traceback
from pathlib import Path

from data_fetchers import (
    fetch_noaa_co2_monthly,
    fetch_met_eireann_warnings,
    fetch_psmsl_dublin_note,
    fetch_nsidc_arctic_daily,
    fetch_noaa_ncei_ohc_latest,
    fetch_forest_fires_data
)
from html_builder import build_html


def main():
    """
    Main function that orchestrates the dashboard generation.
    
    Fetches all climate data from various sources, handles errors gracefully,
    and generates the final HTML dashboard.
    """
    print("🌍 Fetching climate data...")
    
    # Fetch CO₂ data from NOAA
    print("  📊 Fetching CO₂ data...")
    try:
        co2 = fetch_noaa_co2_monthly()
        print(f"    ✅ CO₂: {co2['ppm']} ppm ({co2['year']}-{co2['month']:02d})")
    except Exception as e:
        print(f"    ❌ CO₂ data failed: {e}")
        traceback.print_exc()
        co2 = {
            "year": "N/A", "month": 0, "ppm": float("nan"), 
            "chart": "", "source": "https://gml.noaa.gov/ccgg/trends/"
        }
    
    # Fetch weather warnings from Met Éireann
    print("  🌦️ Fetching weather warnings...")
    try:
        warnings = fetch_met_eireann_warnings()
        print(f"    ✅ Warnings: {warnings['count']} active")
    except Exception as e:
        print(f"    ❌ Weather warnings failed: {e}")
        traceback.print_exc()
        warnings = {
            "count": "N/A", "titles": [], 
            "source": "https://www.met.ie/warnings"
        }
    
    # Get Dublin tide gauge info
    print("  🌊 Getting Dublin tide gauge info...")
    dublin = fetch_psmsl_dublin_note()
    print("    ✅ Dublin tide gauge data available")
    
    # Fetch Arctic sea ice data from NSIDC
    print("  🧊 Fetching Arctic sea ice data...")
    try:
        nsidc = fetch_nsidc_arctic_daily()
        print(f"    ✅ Arctic ice: {nsidc['latest']['extent_mkm2']} million km²")
    except Exception as e:
        print(f"    ❌ Arctic sea ice data failed: {e}")
        traceback.print_exc()
        nsidc = {
            "latest": {"date": "N/A", "extent_mkm2": float("nan")}, 
            "chart": "", "source": "https://nsidc.org/sea-ice-today"
        }
    
    # Fetch ocean heat content from NOAA NCEI
    print("  🌡️ Fetching ocean heat content...")
    try:
        ohc = fetch_noaa_ncei_ohc_latest()
        print(f"    ✅ Ocean heat: {ohc['value']} {ohc['units']} ({ohc['year']})")
    except Exception as e:
        print(f"    ❌ Ocean heat content failed: {e}")
        traceback.print_exc()
        ohc = {
            "year": "N/A", "value": "N/A", "units": "", 
            "source": "https://www.ncei.noaa.gov/access/global-ocean-heat-content/"
        }
    
    # Fetch forest fires data from NASA FIRMS
    print("  🔥 Fetching forest fires data...")
    try:
        fires = fetch_forest_fires_data()
        print(f"    ✅ Forest fires: {fires['count']} active fires detected")
    except Exception as e:
        print(f"    ❌ Forest fires data failed: {e}")
        traceback.print_exc()
        fires = {
            "count": "N/A", 
            "source": "https://firms.modaps.eosdis.nasa.gov/",
            "description": "Fire data temporarily unavailable"
        }
    
    # Build context dictionary
    context = {
        "co2": co2,
        "warnings": warnings, 
        "dublin": dublin,
        "nsidc": nsidc,
        "ohc": ohc,
        "fires": fires
    }
    
    # Generate HTML dashboard
    print("🏗️ Building HTML dashboard...")
    html = build_html(context)
    
    # Write to output file
    output_path = Path("dist") / "index.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ Dashboard generated: {output_path}")
    print("🌐 Open dist/index.html in your browser to view the dashboard!")


if __name__ == "__main__":
    main()
