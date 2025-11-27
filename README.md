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
- **Load residents**: Prefer the Excel sheet `T14` (columns `Postleitzahl` and `Insgesamt`) for exact residents per PLZ. If `T14` is missing, the code falls back to `T5` (Bezirke) and distributes district residents to PLZs (equal-per-PLZ or area-based optional).
- **Merge & visualize**: The app builds two layers — Residents and Charging_Stations — and computes a color scale. Charging station counts are merged into the full PLZ geometry set so PLZs with zero stations are still displayed (legend includes 0 for no charging stations).

**Interpretation of Results**
- **Demand metric**: We compute residents-per-station per PLZ (Einwohner / Number_of_Stations). PLZs with zero stations are treated as infinite demand; these are prioritized because they indicate potential urgent need.
- **Caveats**:
  - The residents total read from `T14` currently sums to `39,026,450` (this appears ~10× too large for Berlin). This likely indicates a parsing/scale issue in the source Excel (e.g., per-1000 values, or repeated aggregation). Verify `plz_einwohner.xlsx` content if exact population totals are required.
  - Geometry centroids are computed in geographic CRS (EPSG:4326). For precise area-based distribution or centroid calculations reproject to a projected CRS (e.g., EPSG:25833) before computing areas/centroids.

Summary totals computed:
- **Total residents (sum of used PLZ entries)**: 39,026,450
- **Total charging stations counted**: 3,657

Top PLZs with ZERO charging stations (sorted by residents — urgent candidates):
- PLZ `10115` — Residents: 283,860 — Stations: 0
- PLZ `14053` — Residents: 2,120 — Stations: 0

Top PLZs by residents-per-station (high demand, excluding zeros):
1. PLZ `12309` — Residents: 177,320 — Stations: 1 — Residents per station: 177,320.0
2. PLZ `12279` — Residents: 175,660 — Stations: 1 — Residents per station: 175,660.0
3. PLZ `12307` — Residents: 134,040 — Stations: 1 — Residents per station: 134,040.0
4. PLZ `13439` — Residents: 228,530 — Stations: 2 — Residents per station: 114,265.0
5. PLZ `10779` — Residents: 93,340 — Stations: 1 — Residents per station: 93,340.0

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
- Verify the `T14` resident totals in `plz_einwohner.xlsx` (the current sum looks suspiciously large). If values are per-1000 or have extra aggregation, adjust parsing accordingly.
- To compute area-proportional distribution (fallback `T5` -> PLZ), reproject `geodata_berlin_plz.csv` to a projected CRS and distribute by polygon area.

**Contact / Credits**

Team 6:
Shoaib Ur Rehman Khan
Chirayu Jain
Muhammed Korkot
Montasir Hasan Chowdhury 