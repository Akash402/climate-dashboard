# Climate Now → 2050 Dashboard (Auto-updating)

This repo hosts a lightweight static dashboard on **GitHub Pages** and **auto-updates weekly** via **GitHub Actions**.

## What updates automatically
- **Mauna Loa CO₂ (monthly)** — fetched from NOAA GML CSV
- **Met Éireann warnings** — fetched from the public JSON feed for Ireland
- **Dublin tide gauge note** — links to PSMSL Station 432 with latest trend reference
- **Timestamp** — when the dashboard was regenerated

## TODO (add later)
- Plug in **NSIDC sea ice extent** numeric (script has a placeholder & link)
- Plug in **Global ocean heat content** (NCEI endpoint)
- Optionally parse **NASA/JPL global mean sea level** latest value

You can also click **Run workflow** in the Actions tab for an immediate refresh.
