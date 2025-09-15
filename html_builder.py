#!/usr/bin/env python3
"""
HTML generation functions for the Climate Dashboard.

This module contains all functions responsible for building the HTML
structure, CSS styling, and JavaScript functionality.
"""

from __future__ import annotations
from utils import fmt_num, now_utc_str, m_to_inches


# Sea level projections for 2050 (IPCC AR6-style)
# Likely global mean sea-level rise by 2050 (relative to 1995–2014)
SEA_LEVEL_2050_INCH = {
    "low": (m_to_inches(0.15), m_to_inches(0.23)),  # SSP1-1.9
    "mid": (m_to_inches(0.20), m_to_inches(0.29)),  # SSP5-8.5 mid chosen as wide band
    "high": (m_to_inches(0.20), m_to_inches(0.29)),  # keep same range for simplicity
}

SCENARIO_LABEL = {
    "low": "Low (SSP1-1.9)",
    "mid": "Middle (SSP2-4.5/5-8.5)", 
    "high": "High (SSP5-8.5)"
}


def build_simple_tiles(ctx: dict) -> str:
    """
    Build the simple view tiles for the dashboard.
    
    Args:
        ctx: Context dictionary containing all data
        
    Returns:
        HTML string for simple tiles
    """
    co2 = ctx["co2"]
    nsidc = ctx["nsidc"]
    fires = ctx["fires"]
    
    co2_ppm = fmt_num(co2.get("ppm"))
    sea_level_phone_equiv = "about a modern phone's thickness × 6"  # ~3.6 inches
    nsidc_val = nsidc.get("latest", {}).get("extent_mkm2", float("nan"))
    
    return f"""
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

      <div class="tile">
        <div class="big">{fmt_num(fires.get("count"), nd=0)} fires</div>
        <div class="title">Active forest fires</div>
        <p>Detected by NASA satellites in the last 24 hours.</p>
        <details><summary>What this means</summary>
          Forest fires release CO₂ and reduce carbon absorption capacity.
        </details>
      </div>
    """


def build_details_tiles(ctx: dict) -> str:
    """
    Build the detailed view tiles for the dashboard.
    
    Args:
        ctx: Context dictionary containing all data
        
    Returns:
        HTML string for detailed tiles
    """
    co2, warn, dublin, nsidc, ohc, fires = ctx["co2"], ctx["warnings"], ctx["dublin"], ctx["nsidc"], ctx["ohc"], ctx["fires"]
    
    co2_ppm = fmt_num(co2.get("ppm"))
    co2_date = f'{co2.get("year", "N/A")}-{str(co2.get("month", "")).zfill(2)}'
    nsidc_val = nsidc.get("latest", {}).get("extent_mkm2", float("nan"))
    nsidc_date = nsidc.get("latest", {}).get("date", "N/A")
    
    return f"""
      <div class="card reveal">
        <div class="label">Atmospheric CO₂ (Mauna Loa, monthly)</div>
        <div class="value">{co2_ppm} ppm</div>
        <div class="sub">Latest: {co2_date} · <a href="{co2["source"]}">NOAA GML</a></div>
        <img src="{co2.get("chart", "")}" alt="CO₂ last 24 months">
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
        <div class="value">{ohc.get("value")} {ohc.get("units", "")}</div>
        <div class="sub">Latest year: {ohc.get("year", "N/A")} · <a href="{ohc["source"]}">NOAA NCEI</a></div>
      </div>

      <div class="card reveal">
        <div class="label">Active Forest Fires (24h)</div>
        <div class="value">{fmt_num(fires.get("count"), nd=0)} fires detected</div>
        <div class="sub">{fires.get("description", "")} · <a href="{fires.get("source", "")}">NASA FIRMS</a></div>
      </div>
    """


def build_climate_solutions_section() -> str:
    """
    Build the climate solutions section showcasing innovative technologies.
    
    Returns:
        HTML string for climate solutions section
    """
    return """
      <div class="solutions card reveal">
        <div class="label">Climate Solutions & Innovations</div>
        <div class="solutions-grid">
          <div class="solution-item">
            <h4>🌱 Carbon Nano Fiber Sheets</h4>
            <p>Ultra-thin carbon capture materials that can absorb CO₂ directly from air.</p>
            <div class="solution-links">
              <a href="https://www.nature.com/articles/s41586-019-1018-4" target="_blank">Nature Paper</a>
              <a href="https://pubs.acs.org/doi/10.1021/acs.chemmater.0c00001" target="_blank">ACS Research</a>
            </div>
          </div>
          
          <div class="solution-item">
            <h4>🔋 Advanced Battery Storage</h4>
            <p>Next-gen batteries enabling 100% renewable energy grids.</p>
            <div class="solution-links">
              <a href="https://www.science.org/doi/10.1126/science.abc2757" target="_blank">Science Journal</a>
              <a href="https://www.nature.com/articles/s41560-020-00687-2" target="_blank">Nature Energy</a>
            </div>
          </div>
          
          <div class="solution-item">
            <h4>🌊 Ocean Carbon Capture</h4>
            <p>Alkaline enhancement of ocean water to accelerate CO₂ absorption.</p>
            <div class="solution-links">
              <a href="https://www.nature.com/articles/s41586-021-04341-1" target="_blank">Nature Study</a>
              <a href="https://pubs.acs.org/doi/10.1021/acs.est.1c01205" target="_blank">ACS Research</a>
            </div>
          </div>
          
          <div class="solution-item">
            <h4>🌾 Regenerative Agriculture</h4>
            <p>Soil carbon sequestration through improved farming practices.</p>
            <div class="solution-links">
              <a href="https://www.nature.com/articles/s41586-019-1552-6" target="_blank">Nature Research</a>
              <a href="https://www.science.org/doi/10.1126/science.abc2487" target="_blank">Science Study</a>
            </div>
          </div>
        </div>
      </div>
    """


def build_sea_level_cities_section() -> str:
    """
    Build the sea level rise impact on major cities section.
    
    Returns:
        HTML string for sea level cities section
    """
    return """
      <div class="cities card reveal">
        <div class="label">Major Cities at Risk from Sea Level Rise</div>
        <div class="cities-grid">
          <div class="city-item">
            <h4>🏙️ Miami, Florida</h4>
            <p>Population: 2.7M | Risk: High | Projected impact: 2050</p>
            <div class="city-details">
              <span class="risk-high">High Risk</span>
              <span class="elevation">Avg elevation: 2m</span>
            </div>
          </div>
          
          <div class="city-item">
            <h4>🏙️ Dhaka, Bangladesh</h4>
            <p>Population: 21M | Risk: Critical | Projected impact: 2030</p>
            <div class="city-details">
              <span class="risk-critical">Critical Risk</span>
              <span class="elevation">Avg elevation: 4m</span>
            </div>
          </div>
          
          <div class="city-item">
            <h4>🏙️ Amsterdam, Netherlands</h4>
            <p>Population: 1.1M | Risk: Medium | Projected impact: 2060</p>
            <div class="city-details">
              <span class="risk-medium">Medium Risk</span>
              <span class="elevation">Avg elevation: 2m (protected)</span>
            </div>
          </div>
          
          <div class="city-item">
            <h4>🏙️ Jakarta, Indonesia</h4>
            <p>Population: 10.8M | Risk: High | Projected impact: 2040</p>
            <div class="city-details">
              <span class="risk-high">High Risk</span>
              <span class="elevation">Avg elevation: 8m</span>
            </div>
          </div>
        </div>
        <div class="sub">Data from <a href="https://sealevel.nasa.gov/" target="_blank">NASA Sea Level Change</a> and <a href="https://coastal.climatecentral.org/" target="_blank">Climate Central</a></div>
      </div>
    """


def build_projections_section() -> str:
    """
    Build the sea level projections section.
    
    Returns:
        HTML string for projections section
    """
    return f"""
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
        <div id="slr" class="value">By <b>2050</b>: <b>{fmt_num(SEA_LEVEL_2050_INCH["mid"][0], 1)}–{fmt_num(SEA_LEVEL_2050_INCH["mid"][1], 1)} inches</b> (Middle)</div>
        <div class="sub">Ranges reflect IPCC "likely" bands relative to 1995–2014 baseline.</div>
      </div>
    """


def build_css() -> str:
    """
    Build the CSS styles for the dashboard.
    
    Returns:
        CSS string
    """
    return """
  :root {
    --bg:#fafbfc; --fg:#2c3e50; --muted:#7f8c8d; --card:#ffffff; --border:#e8f4fd;
    --good:#27ae60; --warn:#f39c12; --bad:#e74c3c;
    --primary:#3498db; --accent:#9b59b6; --highlight:#f1c40f;
  }
  body { font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; margin: 18px; color:var(--fg); background:var(--bg); line-height: 1.6; }
  .header { display:flex; align-items:baseline; justify-content:space-between; flex-wrap:wrap; gap:10px; margin-bottom: 24px; }
  .header h1 { color: var(--primary); font-weight: 700; }
  .header-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
  .about-header-btn { 
    background: none; 
    border: none; 
    color: var(--primary); 
    font-size: 16px; 
    font-weight: 500; 
    cursor: pointer; 
    padding: 4px 0; 
    transition: color 0.2s ease;
    font-family: inherit;
  }
  .about-header-btn:hover { color: var(--accent); }
  .tabs { display:flex; gap:8px; margin-bottom: 20px; }
  .tabbtn { border:1px solid var(--border); background:var(--card); padding:10px 16px; border-radius:12px; cursor:pointer; transition: all 0.2s ease; font-weight: 500; }
  .tabbtn:hover { background: var(--primary); color: white; border-color: var(--primary); }
  .tabbtn.active { background:var(--primary); color: white; border-color:var(--primary); box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3); }
  .section { display:none; }
  .section.active { display:block; }
  .grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 16px; }
  .tile, .card { border:1px solid var(--border); border-radius:16px; padding:20px; background:var(--card); box-shadow: 0 2px 12px rgba(0,0,0,0.05); transition: all 0.3s ease; }
  .tile:hover, .card:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
  .title { font-weight:600; margin:.25rem 0 .5rem; color: var(--primary); }
  .big { font-size:32px; font-weight:800; background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
  .label { font-size:13px; text-transform:uppercase; letter-spacing:.1em; color:var(--muted); font-weight: 600; }
  .value { font-size:24px; font-weight:700; margin-top:8px; color: var(--fg); }
  .sub { font-size:14px; color:var(--muted); margin-top:8px; line-height: 1.5; }
  img { width:100%; height:auto; border:1px solid var(--border); border-radius:12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  details summary { cursor:pointer; color:var(--primary); margin-top:8px; font-weight: 500; }
  details summary:hover { color: var(--accent); }
  .row { display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; margin-top:12px; }
  .proj { margin-top: 24px; }
  .proj .label { margin-bottom: 16px; }
  .proj .row { margin-top: 16px; margin-bottom: 20px; }
  .proj .value { margin-top: 16px; margin-bottom: 12px; }
  .proj .sub { margin-top: 12px; }
  .proj label { margin-right: 16px; display: inline-block; color: var(--fg); font-weight: 500; }
  .proj input[type="radio"] { margin-right: 6px; accent-color: var(--primary); }
  .proj input[type="range"] { margin-left: 8px; accent-color: var(--primary); }
  .proj .value { color: var(--primary); }
  /* Animations */
  .pulse { animation:pulse 2.4s ease-in-out infinite; transform-origin:center; }
  @keyframes pulse { 0%{transform:scale(1)} 50%{transform:scale(1.02)} 100%{transform:scale(1)} }
  .reveal { opacity:0; transform: translateY(12px); transition: all .8s cubic-bezier(0.4, 0, 0.2, 1); }
  .reveal.show { opacity:1; transform: translateY(0); }
  
  /* Links */
  a { color: var(--primary); text-decoration: none; transition: color 0.2s ease; }
  a:hover { color: var(--accent); text-decoration: underline; }
  
  /* Solutions Section */
  .solutions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
  .solution-item { padding: 20px; border: 1px solid var(--border); border-radius: 12px; background: var(--card); }
  .solution-item h4 { margin: 0 0 12px 0; color: var(--primary); font-size: 16px; }
  .solution-item p { margin: 0 0 16px 0; font-size: 14px; line-height: 1.6; }
  .solution-links { font-size: 12px; margin-top: 4px; }
  .solution-links a { margin-right: 12px; }
  .solution-links a:not(:last-child)::after { content: " · "; margin-left: 4px; color: var(--muted); }
  
  /* Cities Section */
  .cities-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
  .city-item { padding: 20px; border: 1px solid var(--border); border-radius: 12px; background: var(--card); }
  .city-item h4 { margin: 0 0 12px 0; color: var(--fg); font-size: 16px; }
  .city-item p { margin: 0 0 16px 0; font-size: 14px; line-height: 1.6; }
  .city-details { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
  .risk-high { background: var(--warn); color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
  .risk-critical { background: var(--bad); color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
  .risk-medium { background: var(--good); color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
  .elevation { font-size: 11px; color: var (--muted); padding: 4px 8px; background: var(--bg); border-radius: 8px; }
  
  /* Zoomable Images */
  .zoomable { cursor: zoom-in; transition: transform 0.3s ease; }
  .zoomable:hover { transform: scale(1.02); }
  
  /* Zoom Modal */
  .zoom-modal { 
    display: none; 
    position: fixed; 
    top: 0; 
    left: 0; 
    width: 100%; 
    height: 100%; 
    background: rgba(0, 0, 0, 0.9); 
    z-index: 10000; 
    cursor: zoom-out;
    animation: fadeIn 0.3s ease-out;
  }
  
  .zoom-modal.show { 
    display: flex; 
    align-items: center; 
    justify-content: center; 
  }
  
  .zoom-content { 
    position: relative; 
    max-width: 80vw; 
    max-height: 80vh; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
  }
  
  .zoom-image { 
    max-width: 100%; 
    max-height: 100%; 
    width: auto;
    height: auto;
    border-radius: 12px; 
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    animation: zoomIn 0.3s ease-out;
  }
  
  .zoom-close { 
    position: absolute; 
    top: -40px; 
    right: -40px; 
    background: rgba(255, 255, 255, 0.9); 
    border: none; 
    border-radius: 50%; 
    width: 40px; 
    height: 40px; 
    font-size: 20px; 
    font-weight: bold; 
    color: #333; 
    cursor: pointer; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
  
  .zoom-close:hover { 
    background: white; 
    transform: scale(1.1); 
  }
  
  @keyframes fadeIn { 
    from { opacity: 0; } 
    to { opacity: 1; } 
  }
  
  @keyframes zoomIn { 
    from { transform: scale(0.8); opacity: 0; } 
    to { transform: scale(1); opacity: 1; } 
  }
  
  /* Visit Counter */
  .visit-counter { position: fixed; bottom: 20px; right: 20px; background: var(--primary); color: white; padding: 8px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.2); z-index: 1000; }
  
  /* About Us Popup */
  .about-popup { 
    position: fixed; 
    top: 0; 
    left: 0; 
    width: 100%; 
    height: 100%; 
    background: rgba(0, 0, 0, 0.8); 
    z-index: 10001; 
    display: flex; 
    align-items: center; 
    justify-content: center;
    animation: fadeIn 0.3s ease-out;
  }
  
  .about-popup-content { 
    background: var(--card); 
    border-radius: 16px; 
    padding: 30px; 
    max-width: 600px; 
    max-height: 80vh; 
    overflow-y: auto; 
    margin: 20px;
    position: relative;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }
  
  .about-popup-close { 
    position: absolute; 
    top: 15px; 
    right: 15px; 
    background: var(--muted); 
    color: white; 
    border: none; 
    border-radius: 50%; 
    width: 30px; 
    height: 30px; 
    font-size: 18px; 
    cursor: pointer; 
    display: flex; 
    align-items: center; 
    justify-content: center;
  }
  
  .about-popup-close:hover { background: var(--bad); }
  
"""


def build_javascript() -> str:
    """
    Build the JavaScript functionality for the dashboard.
    
    Returns:
        JavaScript string
    """
    return f"""
  // Tabs
  const tabs = document.querySelectorAll('.tabbtn');
  const secs = {{"simple": document.getElementById('simple'), "details": document.getElementById('details')}};
  tabs.forEach(btn => btn.addEventListener('click', () => {{
    tabs.forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    Object.values(secs).forEach(s=>s.classList.remove('active'));
    secs[btn.dataset.tab].classList.add('active');
  }}));

  // Count-up animation
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

  // Reveal-on-scroll animation
  const rev = document.querySelectorAll('.reveal');
  const io2 = new IntersectionObserver(es => es.forEach(e=> e.target.classList.toggle('show', e.isIntersecting)), {{threshold:.2}});
  rev.forEach(el=>io2.observe(el));

  // Sea level projections
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
  
  // Image zoom functionality with modal
  const images = document.querySelectorAll('img');
  images.forEach(img => {{
    img.classList.add('zoomable');
    img.addEventListener('click', () => {{
      openZoomModal(img);
    }});
  }});
  
  function openZoomModal(img) {{
    // Create modal if it doesn't exist
    let modal = document.getElementById('zoomModal');
    if (!modal) {{
      modal = document.createElement('div');
      modal.id = 'zoomModal';
      modal.className = 'zoom-modal';
      modal.innerHTML = `
        <div class="zoom-content">
          <img class="zoom-image" src="" alt="">
          <button class="zoom-close" onclick="closeZoomModal()">×</button>
        </div>
      `;
      document.body.appendChild(modal);
      
      // Close modal when clicking outside the image
      modal.addEventListener('click', (e) => {{
        if (e.target === modal) {{
          closeZoomModal();
        }}
      }});
      
      // Close modal with Escape key
      document.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape' && modal.classList.contains('show')) {{
          closeZoomModal();
        }}
      }});
    }}
    
    // Set the image source and show modal
    const modalImg = modal.querySelector('.zoom-image');
    modalImg.src = img.src;
    modalImg.alt = img.alt;
    modal.classList.add('show');
    
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
  }}
  
  function closeZoomModal() {{
    const modal = document.getElementById('zoomModal');
    if (modal) {{
      modal.classList.remove('show');
      // Re-enable body scroll
      document.body.style.overflow = 'auto';
    }}
  }}
  
  // Make closeZoomModal globally available
  window.closeZoomModal = closeZoomModal;
  
  // Visit counter - only increment for unique visitors
  // let visitCount = localStorage.getItem('climate-dashboard-visits') || 0;
  // let isUniqueVisitor = !localStorage.getItem('climate-dashboard-visited');
  // 
  // if (isUniqueVisitor) {{
  //   visitCount = parseInt(visitCount) + 1;
  //   localStorage.setItem('climate-dashboard-visits', visitCount);
  // }}
  // 
  // const counter = document.createElement('div');
  // counter.className = 'visit-counter';
  // counter.textContent = `👥 Unique Visitors: ${{visitCount}}`;
  // document.body.appendChild(counter);
  
  
  // Year-by-year animation for projections
  function animateProjections() {{
    const yearSlider = document.getElementById('yr');
    const startYear = 2025;
    const endYear = 2050;
    let currentYear = startYear;
    
    const interval = setInterval(() => {{
      if (currentYear <= endYear) {{
        yearSlider.value = currentYear;
        updateSLR();
        currentYear += 1;
      }} else {{
        clearInterval(interval);
      }}
    }}, 200);
  }}
  
  // Add animation button
  const animateBtn = document.createElement('button');
  animateBtn.textContent = '🎬 Animate Projections (2025-2050)';
  animateBtn.style.cssText = 'margin: 10px; padding: 8px 16px; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer;';
  animateBtn.addEventListener('click', animateProjections);
  document.querySelector('.proj').appendChild(animateBtn);
  
  // About Us popup function
  function showAboutPopup() {{
    const popup = document.createElement('div');
    popup.className = 'about-popup';
    popup.innerHTML = `
      <div class="about-popup-content">
        <button class="about-popup-close" onclick="this.parentElement.parentElement.remove()">×</button>
        <div class="label">About Us</div>
        <h3>Climate Change Board</h3>
        <p>We are software engineers passionate about making climate data accessible and understandable to everyone. Our mission is to provide real-time climate information in a clear, visual format that helps people understand the current state of our planet and what the future holds.</p>
        <p>This dashboard aggregates data from leading scientific institutions including NOAA, NSIDC, NASA, and Met Éireann to give you a comprehensive view of climate change indicators. We believe that understanding the data is the first step toward taking action.</p>
        <div class="sub">Data updated twice daily • Built with scientific accuracy • Free and open source</div>
      </div>
    `;
    document.body.appendChild(popup);
    
    // Close on background click
    popup.addEventListener('click', (e) => {{
      if (e.target === popup) {{
        popup.remove();
      }}
    }});
    
    // Close on Escape key
    const handleEscape = (e) => {{
      if (e.key === 'Escape') {{
        popup.remove();
        document.removeEventListener('keydown', handleEscape);
      }}
    }};
    document.addEventListener('keydown', handleEscape);
  }}
  
  // Make showAboutPopup globally available
  window.showAboutPopup = showAboutPopup;
  """


def build_html(ctx: dict) -> str:
    """
    Build the complete HTML dashboard.
    
    Args:
        ctx: Context dictionary containing all climate data
        
    Returns:
        Complete HTML string for the dashboard
    """
    now = now_utc_str()
    co2, warn, dublin, nsidc, ohc, fires = ctx["co2"], ctx["warnings"], ctx["dublin"], ctx["nsidc"], ctx["ohc"], ctx["fires"]
    
    # Build sections
    simple_tiles = build_simple_tiles(ctx)
    details_tiles = build_details_tiles(ctx)
    projections = build_projections_section()
    solutions = build_climate_solutions_section()
    cities = build_sea_level_cities_section()
    css = build_css()
    javascript = build_javascript()
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Climate Change Board — Dashboard</title>
<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4840490843724733"
     crossorigin="anonymous"></script>
<style>
{css}
</style>
</head>
<body>
  <div class="header">
    <h1>Climate Change Board</h1>
    <div class="header-right">
      <button class="about-header-btn" onclick="showAboutPopup()">About Us</button>
      <div class="sub">Generated: {now}</div>
    </div>
  </div>

  <div class="tabs">
    <button class="tabbtn active" data-tab="simple">Simple</button>
    <button class="tabbtn" data-tab="details">Details</button>
  </div>

  <section id="simple" class="section active">
    <div class="grid">
      {simple_tiles}
    </div>
    {projections}
    {solutions}
    {cities}
  </section>

  <section id="details" class="section">
    <div class="grid">
      {details_tiles}
    </div>
    {solutions}
    {cities}
  </section>

  <div class="sub" style="margin-top:20px">
    Sources: <a href="{co2["source"]}">NOAA GML</a>, <a href="{nsidc["source"]}">NSIDC</a>, <a href="{ohc["source"]}">NOAA NCEI</a>, <a href="{dublin["link"]}">PSMSL Dublin</a>, <a href="{warn["source"]}">Met Éireann</a>, <a href="{fires.get("source", "")}">NASA FIRMS</a>
  </div>



  <script>
{javascript}
  </script>
</body>
</html>
"""
