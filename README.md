**Project Introduction**
- **Name**: Berlin Geo Heatmap (Project 1)
- **Purpose**: Visualize the heatmap for the amount of electric charging stations and residents. With this information a 3rd heatmap is being generated to show the demand defined by residents/charging station.

**Program Structure**
- **Main app**: `main.py` — Streamlit app orchestrator that loads datasets, preprocesses them, and builds the interactive map.
- **Configuration**: `config.py` — small dictionary `pdict` with filenames and the geocode key (`PLZ`).
- **Core code**: `berlingeoheatmap_project1\core\methods.py` — preprocessing and map-building functions.
- **Helpers**: `berlingeoheatmap_project1\core\HelperTools.py` — timing and small utilities.
- **Datasets folder**: `berlingeoheatmap_project1\datasets`
  - PLZ polygons: `geodata_berlin_plz.csv` (WKT geometry)
  - Charging stations registry: `Ladesaeulenregister.csv` (original registry with metadata header lines)
  - Residents: `plz_einwohner.xlsx` (sheet `T14` is preferred for per-PLZ counts, this has been added manually because there was no csv for this given. Also this dataset is more up to date)
  - Bezirke shapefiles: `datasets\berlin_bezirke\bezirksgrenzen.shp` (used for T5 fallback mapping, contains residents per district)

**How It Works (High Level)**
- **Load geodata**: PLZ polygons from `geodata_berlin_plz.csv` are loaded and used to draw PLZ areas and compute centroids.
- **Load charging stations**: `Ladesaeulenregister.csv` is read with header-detection (file contains metadata rows). Charging station rows are preprocessed and assigned to PLZs.
- **Load residents**: Prefer the Excel sheet `T14` (columns `Postleitzahl` and `Insgesamt`) for exact residents per (PLZ, district) combination. Each row represents residents in that postal code within that district. If `T14` is missing, the code falls back to `T5` (Bezirke) and distributes district residents to PLZs.
- **Merge & visualize**: The app builds three interactive layers — **Residents**, **Charging_Stations**, and **Demand** — with color scales. Charging station counts are merged into the full PLZ geometry set so PLZs with zero stations are still displayed (legend includes 0). Demand shows residents per charging station per PLZ (color-scaled to 95th percentile to avoid outlier saturation).

**Interpretation of Results**
- **Residents layer**: Shows population density by (PLZ, district) combination. Each row in T14 represents a unique postal code within a district.
- **Charging Stations layer**: Shows the count of electric vehicle charging stations per PLZ. PLZs with zero stations are displayed in yellow to highlight gaps in infrastructure.
- **Demand layer**: Computed metric = residents / charging stations per PLZ. Color scale is capped at the 95th percentile to avoid outlier saturation and make patterns visible. High demand (red) indicates areas with many residents but few charging stations — priorities for infrastructure expansion.
- **Data integrity**: The residents total from `T14` is **3,902,645** (verified correct). Each (PLZ, district) entry is counted separately; do NOT aggregate by PLZ alone.

Summary totals computed:
- **Total residents (sum of all T14 rows)**: 3,902,645
- **Total charging stations counted**: 3,657

Top PLZs by residents per station (high demand, highest ratio first):
- PLZ `12309` — Residents: 28,386 — Stations: 1 — Demand (res/station): 28,386
- PLZ `10247` — Residents: 41,630 — Stations: 2 — Demand: 20,815
- PLZ `13187` — Residents: 38,144 — Stations: 2 — Demand: 19,072
- PLZ `12627` — Residents: 45,930 — Stations: 3 — Demand: 15,310

Note: PLZs with zero charging stations (e.g., parts of districts with very small resident populations in certain PLZ ranges) also show high demand but are not always the largest population centers.

Full detailed demand rankings saved to `tmp_plz_demand.csv` (regenerate by running `scripts/compute_demand.py`).

**How to run the app (recommended, from project root)**
PowerShell (no activation required if you call python in .venv explicitly):
```
.\.venv\Scripts\python.exe -m streamlit run .\main.py --server.port 8503
```
Or activate the venv then run:
```
.\.venv\Scripts\Activate.ps1
streamlit run .\main.py --server.port 8503
```

**Notes & Next Steps**
- Data quality: Residents are from official Berlin statistics (T14, updated June 2025); charging stations from federal registry (Ladesaeulenregister).
- Geometry: PLZ polygons are in geographic CRS (EPSG:4326). For precise area-proportional calculations, reproject to a projected CRS (e.g., EPSG:25833).
- Warning suppression: Some pandas/geopandas warnings (SettingWithCopyWarning, CRS warnings) can be cleaned by specifying dtypes and using `.loc` assignments. See code comments for details.

**Contact / Credits**

Team 6:
- Shoaib Ur Rehman Khan
- Chirayu Jain
- Muhammed Korkot
- Montasir Hasan Chowdhury 