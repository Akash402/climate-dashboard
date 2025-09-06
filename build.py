#!/usr/bin/env python3
"""
Climate Now → 2050 — static dashboard (friendly UI)
Features:
- Simple/Details views
- Count-up animations, reveal-on-scroll
- Scenario toggle (Low/Mid/High) + year slider for sea-level projection
- Plain-language explanations + friendly units
- Robust fetchers with graceful fallback

Run:
  pip install -r requirements.txt
  python build.py
"""

from __future__ import annotations
import io, gzip, traceback
from pathlib import Path
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests
import pandas as pd
import numpy as np

OUT = Path("dist")
OUT.mkdir(parents=True, exist_ok=True)

# ------------------ Helpers ------------------
def http_get(url: str, timeout=30, allow_redirects=True) -> requests.Response:
    r = requests.get(url, timeout=timeout, allow_redirects=allow_redirects,
        headers={"User-Agent": "climate-dashboard/1.2 (+github actions)"})
    r.raise_for_status()
    return r

def try_urls(urls, timeout=45, binary=False):
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

def fmt_num(val, nd=2, default="—"):
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return default
        if isinstance(val, (int, np.integer)):
            return f"{val}"
        return f"{float(val):.{nd}f}"
    except Exception:
        return default

# Unit helpers
def mm_to_inches(mm): return mm / 25.4
def m_to_inches(m): return m * 39.3701

# ------------------ Data fetchers ------------------
def fetch_noaa_co2_monthly():
    url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"
    r = http_get(url)
    lines = [ln for ln in r.text.splitlines() if ln.strip() and not ln.startswith("#")]
    df = pd.read_csv(io.StringIO("\n".join(lines)), header=None)
    cols = ["year","month","decimal_date","average","deseasonalized","num_days","stdev","uncertainty"]
    if df.shape[1] > len(cols): cols += list(range(len(cols), df.shape[1]))
    df.columns = cols
    df = df.replace(-99.99, np.nan).dropna(subset=["average"])
    latest = df.iloc[-1]
    latest_ppm = float(latest["average"])
    latest_year = int(latest["year"]); latest_month = int(latest["month"])

    tail = df.tail(24).copy()
    dates = pd.to_datetime(
        tail["year"].astype(int).astype(str) + "-" + tail["month"].astype(int).astype(str) + "-15",
        errors="coerce",
    )
    fig = plt.figure()
    plt.plot(dates, tail["average"], marker="o")
    plt.title("Mauna Loa CO₂ (last 24 months)")
    plt.ylabel("ppm"); plt.xlabel("")
    plt.grid(True, alpha=0.3)
    save_png(fig, OUT / "co2_24mo.png")

    return {"year": latest_year, "month": latest_month, "ppm": latest_ppm,
            "chart": "co2_24mo.png", "source": "https://gml.noaa.gov/ccgg/trends/"}

def fetch_met_eireann_warnings():
    url = "https://www.met.ie/Open_Data/json/warning_IRELAND.json"
    try:
        data = http_get(url, timeout=30).json()
        items = data.get("warnings", []) or []
        active = [w for w in items if (w.get("status","") or "").lower() == "active"]
        titles = [w.get("title") for w in active if w.get("title")] or []
        return {"count": len(active), "titles": titles[:3], "source":"https://www.met.ie/warnings"}
    except Exception:
        return {"count": "N/A", "titles": [], "source":"https://www.met.ie/warnings"}

def fetch_psmsl_dublin_note():
    return {"link":"https://psmsl.org/data/obtaining/stations/432.php",
            "note":"Dublin tide-gauge shows a gradual long-term rise."}

def _parse_nsidc_daily_csv(text: str):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    start_idx = 0
    for i, ln in enumerate(lines):
        if ln.lower().startswith("year") or ln.lower().startswith("yyyy"):
            start_idx = i; break
    csv_text = "\n".join(lines[start_idx:])
    df = pd.read_csv(io.StringIO(csv_text))
    ycol = next((c for c in df.columns if c.lower().startswith("y")), None)
    mcol = next((c for c in df.columns if c.lower().startswith("m")), None)
    dcol = next((c for c in df.columns if c.lower().startswith("d")), None)
    ecol = next((c for c in df.columns if "extent" in c.lower()), None)
    if not all([ycol, mcol, dcol, ecol]): raise ValueError("Unexpected NSIDC CSV columns")
    df["date"] = pd.to_datetime(
        df[ycol].astype(int).astype(str) + "-" + df[mcol].astype(int).astype(str) + "-" + df[dcol].astype(int).astype(str),
        errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    df = df.replace(-9999, np.nan)
    return df, ecol

def fetch_nsidc_arctic_daily():
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
                text = gzip.decompress(content).decode("utf-8","replace")
            else:
                _, text = try_urls([url], binary=False)
            df, ecol = _parse_nsidc_daily_csv(text)
            latest_row = df.dropna(subset=[ecol]).iloc[-1]
            latest_val = float(latest_row[ecol]); latest_date = str(latest_row["date"].date())
            tail = df.dropna(subset=[ecol]).tail(365).copy()
            fig = plt.figure()
            plt.plot(tail["date"], tail[ecol])
            plt.title("Arctic Sea Ice Extent (last 365 days)")
            plt.ylabel("million km²"); plt.xlabel("")
            plt.grid(True, alpha=0.3)
            save_png(fig, OUT / "arctic_extent_365d.png")
            return {"latest":{"date":latest_date,"extent_mkm2":latest_val},
                    "chart":"arctic_extent_365d.png","source":"https://nsidc.org/sea-ice-today"}
        except Exception:
            continue
    return {"latest":{"date":"N/A","extent_mkm2":float("nan")},"chart":"","source":"https://nsidc.org/sea-ice-today"}

def fetch_noaa_ncei_ohc_latest():
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
            if not num_cols: continue
            df = df.dropna(subset=num_cols).sort_values(year_col)
            last = df.iloc[-1]
            latest_year = int(last[year_col]); latest_val = float(last[num_cols[0]])
            return {"year": latest_year, "value": latest_val, "units": "J × 10^22",
                    "source":"https://www.ncei.noaa.gov/access/global-ocean-heat-content/"}
        except Exception:
            continue
    return {"year":"N/A","value":"N/A","units":"","source":"https://www.ncei.noaa.gov/access/global-ocean-heat-content/"}

# ------------------ Projections (IPCC AR6–style) ------------------
# Likely global mean sea-level rise by 2050 (relative to 1995–2014)
SEA_LEVEL_2050_INCH = {
    "low":  (m_to_inches(0.15), m_to_inches(0.23)),  # SSP1-1.9
    "mid":  (m_to_inches(0.20), m_to_inches(0.29)),  # SSP5-8.5 mid chosen as wide band
    "high": (m_to_inches(0.20), m_to_inches(0.29)),  # keep same range for simplicity
}
SCENARIO_LABEL = {"low":"Low (SSP1-1.9)","mid":"Middle (SSP2-4.5/5-8.5)","high":"High (SSP5-8.5)"}

# ------------------ HTML builder ------------------
def build_html(ctx: dict) -> str:
    now = now_utc_str()
    co2, warn, dublin, nsidc, ohc = ctx["co2"], ctx["warnings"], ctx["dublin"], ctx["nsidc"], ctx["ohc"]

    # Friendly strings
    co2_ppm = fmt_num(co2.get("ppm"))
    co2_date = f'{co2.get("year","N/A")}-{str(co2.get("month","")).zfill(2)}'
    sea_level_phone_equiv = "about a modern phone’s thickness × 6"  # ~3.6 inches
    nsidc_val = nsidc.get("latest",{}).get("extent_mkm2", float("nan"))
    nsidc_date = nsidc.get("latest",{}).get("date","N/A")

    # Simple/Details tiles
    simple_tiles = f"""
      <div class="tile pulse">
        <div class="big"><span class="count" data-value="{co2_ppm}">0</span> ppm</div>
        <div class="title">CO₂ in the air</div>
        <p>Higher than at any point in human history.</p>
        <details><summary>What this means</summary>
          CO₂ traps heat. More CO₂ → warmer planet.
        </details>
      </div>

      <div class="tile">
        <div class="big">+3.6 inches</div>
        <div class="title">Sea level since 1993</div>
        <p>Global seas have risen by ~9.2 cm — {sea_level_phone_equiv}.</p>
        <details><summary>What this means</summary>
          Higher baseline makes coastal flooding more frequent.
        </details>
      </div>

      <div class="tile">
        <div class="big">{fmt_num(nsidc_val)} million km²</div>
        <div class="title">Arctic summer ice</div>
        <p>Trending lower; darker ocean absorbs more heat.</p>
        <details><summary>What this means</summary>
          Less ice → more warming feedback.
        </details>
      </div>

      <div class="tile">
        <div class="big">Oceans are the heat sponge</div>
        <div class="title">Ocean heat content</div>
        <p>Most extra heat is stored in the upper 2 km of the ocean.</p>
        <details><summary>What this means</summary>
          Warmer oceans raise sea levels and power heavier downpours.
        </details>
      </div>
    """

    details_tiles = f"""
      <div class="card reveal">
        <div class="label">Atmospheric CO₂ (Mauna Loa, monthly)</div>
        <div class="value">{co2_ppm} ppm</div>
        <div class="sub">Latest: {co2_date} · <a href="{co2["source"]}">NOAA GML</a></div>
        <img src="{co2.get("chart","")}" alt="CO₂ last 24 months">
      </div>

      <div class="card reveal">
        <div class="label">Met Éireann Warnings (Ireland)</div>
        <div class="value">{fmt_num(warn.get("count"), nd=0)}</div>
        <div class="sub">{", ".join(warn.get("titles") or []) or "—"} · <a href="{warn["source"]}">Source</a></div>
      </div>

      <div class="card reveal">
        <div class="label">Arctic Sea Ice Extent</div>
        <div class="value">{fmt_num(nsidc_val)} million km²</div>
        <div class="sub">Latest: {nsidc_date} · <a href="{nsidc["source"]}">NSIDC</a></div>
        {f'<img src="{nsidc.get("chart")}" alt="Arctic sea-ice extent sparkline">' if nsidc.get("chart") else "<div class='sub'>Chart unavailable this run.</div>"}
      </div>

      <div class="card reveal">
        <div class="label">Dublin Tide Gauge</div>
        <div class="value">{dublin["note"]}</div>
        <div class="sub"><a href="{dublin["link"]}">PSMSL Station 432</a></div>
      </div>

      <div class="card reveal">
        <div class="label">Ocean Heat Content (0–2000 m)</div>
        <div class="value">{ohc.get("value")} {ohc.get("units","")}</div>
        <div class="sub">Latest year: {ohc.get("year","N/A")} · <a href="{ohc["source"]}">NOAA NCEI</a></div>
      </div>
    """

    # Projections UI (sea level)
    proj_html = f"""
      <div class="proj card reveal">
        <div class="label">Sea level projection</div>
        <div class="row">
          <div>
            <label><input type="radio" name="scn" value="low"> Low</label>
            <label><input type="radio" name="scn" value="mid" checked> Middle</label>
            <label><input type="radio" name="scn" value="high"> High</label>
          </div>
          <div>
            <label>Projection year: <input id="yr" type="range" min="2025" max="2050" value="2050"></label>
          </div>
        </div>
        <div id="slr" class="value">By <b>2050</b>: <b>{fmt_num(SEA_LEVEL_2050_INCH["mid"][0],1)}–{fmt_num(SEA_LEVEL_2050_INCH["mid"][1],1)} inches</b> (Middle)</div>
        <div class="sub">Ranges reflect IPCC “likely” bands relative to 1995–2014 baseline.</div>
      </div>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Climate Now & to 2050 — Dashboard</title>
<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-YOUR_PUBLISHER_ID"
     crossorigin="anonymous"></script>
<style>
  :root {{
    --bg:#fafbfc; --fg:#2c3e50; --muted:#7f8c8d; --card:#ffffff; --border:#e8f4fd;
    --good:#27ae60; --warn:#f39c12; --bad:#e74c3c;
    --primary:#3498db; --accent:#9b59b6; --highlight:#f1c40f;
  }}
  body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; margin: 18px; color:var(--fg); background:var(--bg); line-height: 1.6; }}
  .header {{ display:flex; align-items:baseline; justify-content:space-between; flex-wrap:wrap; gap:10px; margin-bottom: 24px; }}
  .header h1 {{ color: var(--primary); font-weight: 700; }}
  .tabs {{ display:flex; gap:8px; margin-bottom: 20px; }}
  .tabbtn {{ border:1px solid var(--border); background:var(--card); padding:10px 16px; border-radius:12px; cursor:pointer; transition: all 0.2s ease; font-weight: 500; }}
  .tabbtn:hover {{ background: var(--primary); color: white; border-color: var(--primary); }}
  .tabbtn.active {{ background:var(--primary); color: white; border-color:var(--primary); box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3); }}
  .section {{ display:none; }}
  .section.active {{ display:block; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 16px; }}
  .tile, .card {{ border:1px solid var(--border); border-radius:16px; padding:20px; background:var(--card); box-shadow: 0 2px 12px rgba(0,0,0,0.05); transition: all 0.3s ease; }}
  .tile:hover, .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
  .title {{ font-weight:600; margin:.25rem 0 .5rem; color: var(--primary); }}
  .big {{ font-size:32px; font-weight:800; background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
  .label {{ font-size:13px; text-transform:uppercase; letter-spacing:.1em; color:var(--muted); font-weight: 600; }}
  .value {{ font-size:24px; font-weight:700; margin-top:8px; color: var(--fg); }}
  .sub {{ font-size:14px; color:var(--muted); margin-top:8px; line-height: 1.5; }}
  img {{ width:100%; height:auto; border:1px solid var(--border); border-radius:12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  details summary {{ cursor:pointer; color:var(--primary); margin-top:8px; font-weight: 500; }}
  details summary:hover {{ color: var(--accent); }}
  .row {{ display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; margin-top:12px; }}
  .proj {{ margin-top: 24px; }}
  .proj .label {{ margin-bottom: 16px; }}
  .proj .row {{ margin-top: 16px; margin-bottom: 20px; }}
  .proj .value {{ margin-top: 16px; margin-bottom: 12px; }}
  .proj .sub {{ margin-top: 12px; }}
  .proj label {{ margin-right: 16px; display: inline-block; color: var(--fg); font-weight: 500; }}
  .proj input[type="radio"] {{ margin-right: 6px; accent-color: var(--primary); }}
  .proj input[type="range"] {{ margin-left: 8px; accent-color: var(--primary); }}
  .proj .value {{ color: var(--primary); }}
  /* Animations */
  .pulse {{ animation:pulse 2.4s ease-in-out infinite; transform-origin:center; }}
  @keyframes pulse {{ 0%{{transform:scale(1)}} 50%{{transform:scale(1.02)}} 100%{{transform:scale(1)}} }}
  .reveal {{ opacity:0; transform: translateY(12px); transition: all .8s cubic-bezier(0.4, 0, 0.2, 1); }}
  .reveal.show {{ opacity:1; transform: translateY(0); }}
  
  /* Links */
  a {{ color: var(--primary); text-decoration: none; transition: color 0.2s ease; }}
  a:hover {{ color: var(--accent); text-decoration: underline; }}
</style>
</head>
<body>
  <div class="header">
    <h1>Climate Now & to 2050</h1>
    <div class="sub">Generated: {now}</div>
  </div>

  <!-- AdSense Banner Ad -->
  <div style="margin: 20px 0; text-align: center;">
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-YOUR_PUBLISHER_ID"
         data-ad-slot="YOUR_AD_SLOT_ID"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({{}});
    </script>
  </div>

  <div class="tabs">
    <button class="tabbtn active" data-tab="simple">Simple</button>
    <button class="tabbtn" data-tab="details">Details</button>
  </div>

  <section id="simple" class="section active">
    <div class="grid">
      {simple_tiles}
    </div>
    {proj_html}
  </section>

  <section id="details" class="section">
    <div class="grid">
      {details_tiles}
    </div>
  </section>

  <div class="sub" style="margin-top:20px">
    Sources: <a href="{co2["source"]}">NOAA GML</a>, <a href="{nsidc["source"]}">NSIDC</a>, <a href="{ohc["source"]}">NOAA NCEI</a>, <a href="{dublin["link"]}">PSMSL Dublin</a>, Met Éireann warnings.
  </div>

  <!-- AdSense Footer Ad -->
  <div style="margin: 20px 0; text-align: center;">
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-YOUR_PUBLISHER_ID"
         data-ad-slot="YOUR_FOOTER_AD_SLOT_ID"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({{}});
    </script>
  </div>

  <script>
  // Tabs
  const tabs = document.querySelectorAll('.tabbtn');
  const secs = {{"simple": document.getElementById('simple'), "details": document.getElementById('details')}};
  tabs.forEach(btn => btn.addEventListener('click', () => {{
    tabs.forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    Object.values(secs).forEach(s=>s.classList.remove('active'));
    secs[btn.dataset.tab].classList.add('active');
  }}));

  // Count-up
  const ease = t => 1 - Math.pow(1-t, 3);
  const counts = [...document.querySelectorAll('.count')];
  const io1 = new IntersectionObserver(es => es.forEach(e=>{{
    if (!e.isIntersecting) return;
    const el = e.target; io1.unobserve(el);
    const end = parseFloat(el.dataset.value); const start = 0, dur = 1000; let t0;
    function tick(ts){{ t0 ??= ts; const p = Math.min(1,(ts-t0)/dur); el.textContent = (start+(end-start)*ease(p)).toFixed(end%1?1:0); if(p<1) requestAnimationFrame(tick); }}
    requestAnimationFrame(tick);
  }}), {{threshold:.6}});
  counts.forEach(el=>io1.observe(el));

  // Reveal-on-scroll
  const rev = document.querySelectorAll('.reveal');
  const io2 = new IntersectionObserver(es => es.forEach(e=> e.target.classList.toggle('show', e.isIntersecting)), {{threshold:.2}});
  rev.forEach(el=>io2.observe(el));

  // Projections (simple string swap; not a simulation)
  const SLR = {{
    low:  [{SEA_LEVEL_2050_INCH["low"][0]:.1f}, {SEA_LEVEL_2050_INCH["low"][1]:.1f}],
    mid:  [{SEA_LEVEL_2050_INCH["mid"][0]:.1f}, {SEA_LEVEL_2050_INCH["mid"][1]:.1f}],
    high: [{SEA_LEVEL_2050_INCH["high"][0]:.1f}, {SEA_LEVEL_2050_INCH["high"][1]:.1f}],
  }};
  const SCN_LABEL = {{ low:"Low", mid:"Middle", high:"High" }};
  let scenario = "mid";
  const slr = document.getElementById('slr');
  const yr = document.getElementById('yr');
  function updateSLR(){{
    const y = yr.value;
    const vals = SLR[scenario];
    const lo = vals[0], hi = vals[1];
    slr.innerHTML = 'By <b>' + y + '</b>: <b>' + lo + '–' + hi + ' inches</b> (' + SCN_LABEL[scenario] + ')';
  }}
  document.querySelectorAll('input[name="scn"]').forEach(r => r.addEventListener('change', e => {{ scenario = e.target.value; updateSLR(); }}));
  yr.addEventListener('input', updateSLR); updateSLR();
  </script>
</body>
</html>
"""
    return html

# ------------------ Main ------------------
def main():
    try:
        co2 = fetch_noaa_co2_monthly()
    except Exception:
        traceback.print_exc()
        co2 = {"year":"N/A","month":0,"ppm":float("nan"),"chart":"","source":"https://gml.noaa.gov/ccgg/trends/"}
    try:
        warnings = fetch_met_eireann_warnings()
    except Exception:
        traceback.print_exc()
        warnings = {"count":"N/A","titles":[],"source":"https://www.met.ie/warnings"}
    dublin = fetch_psmsl_dublin_note()
    try:
        nsidc = fetch_nsidc_arctic_daily()
    except Exception:
        traceback.print_exc()
        nsidc = {"latest":{"date":"N/A","extent_mkm2":float("nan")},"chart":"","source":"https://nsidc.org/sea-ice-today"}
    try:
        ohc = fetch_noaa_ncei_ohc_latest()
    except Exception:
        traceback.print_exc()
        ohc = {"year":"N/A","value":"N/A","units":"","source":"https://www.ncei.noaa.gov/access/global-ocean-heat-content/"}

    html = build_html({"co2":co2,"warnings":warnings,"dublin":dublin,"nsidc":nsidc,"ohc":ohc})
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("Wrote", OUT / "index.html")

if __name__ == "__main__":
    main()
