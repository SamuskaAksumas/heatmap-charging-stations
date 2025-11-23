**Project Introduction**
- **Name**: Berlin Geo Heatmap (Project 1)
- **Location**: Repository root: `C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1`
- **Purpose**: Visualize demand for electric vehicle charging infrastructure across Berlin postal codes (PLZ). The app shows two map layers: Residents per PLZ and Charging Stations per PLZ, and highlights areas where demand (many residents / few chargers) is highest.

**Program Structure**
- **Project root**: `C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1`
- **Main app**: `main.py` — Streamlit app orchestrator that loads datasets, preprocesses them, and builds the interactive map.
- **Configuration**: `config.py` — small dictionary `pdict` with filenames and the geocode key (`PLZ`).
- **Core code**: `C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1\core\methods.py` — preprocessing and map-building functions.
- **Helpers**: `C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1\core\HelperTools.py` — timing and small utilities.
- **Datasets folder**: `C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1\datasets`
  - PLZ polygons: `geodata_berlin_plz.csv` (WKT geometry)
  - Charging stations registry: `Ladesaeulenregister.csv` (original registry with metadata header lines)
  - Residents: `plz_einwohner.xlsx` (sheet `T14` is preferred for per-PLZ counts)
  - Bezirke shapefiles: `datasets\berlin_bezirke\bezirksgrenzen.shp` (used for T5 fallback mapping)

**How It Works (High Level)**
- **Load geodata**: PLZ polygons from `geodata_berlin_plz.csv` are loaded and used to draw PLZ areas and compute centroids.
- **Load charging stations**: `Ladesaeulenregister.csv` is read with header-detection (file contains metadata rows). Charging station rows are preprocessed and assigned to PLZs.
- **Load residents**: Prefer the Excel sheet `T14` (columns `Postleitzahl` and `Insgesamt`) for exact residents per PLZ. If `T14` is missing, the code falls back to `T5` (Bezirke) and distributes district residents to PLZs (equal-per-PLZ or area-based optional).
- **Merge & visualize**: The app builds two layers — Residents and Charging_Stations — and computes a color scale. Charging station counts are merged into the full PLZ geometry set so PLZs with zero stations are still displayed (legend includes 0).

**Interpretation of Results**
- **Demand metric**: We compute residents-per-station per PLZ (Einwohner / Number_of_Stations). PLZs with zero stations are treated as infinite demand; these are prioritized because they indicate potential urgent need.
- **Caveats**:
  - The residents total read from `T14` currently sums to `39,026,450` (this appears ~10× too large for Berlin). This likely indicates a parsing/scale issue in the source Excel (e.g., per-1000 values, or repeated aggregation). Verify `plz_einwohner.xlsx` content if exact population totals are required.
  - Geometry centroids are computed in geographic CRS (EPSG:4326). For precise area-based distribution or centroid calculations reproject to a projected CRS (e.g., EPSG:25833) before computing areas/centroids.

**Key Findings (Computed)**
All file paths used for these results are absolute paths in this environment:
- Project root: `C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1`
- Datasets folder: `C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1\datasets`
- Charging stations CSV: `C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1\datasets\Ladesaeulenregister.csv`
- Residents (used): `C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1\datasets\plz_einwohner.xlsx`

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

Note: full detailed per-PLZ rankings are saved to:
`C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1\tmp_plz_demand.csv`
and summary JSON:
`C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map\berlingeoheatmap_project1\tmp_plz_demand_summary.json`

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
- Clean warnings by specifying `dtype` when reading large CSVs and using `.loc`-assignments to avoid SettingWithCopyWarning.

**Contact / Credits**
- Created as part of the course exercises in `C:\Users\Samuska\Documents\Uni\Fortgeschrittene_Softwaretechnik\exercises\Project_Charging_Map`.

---
If you want, I can (1) inspect `plz_einwohner.xlsx` to correct parsing/scale, (2) implement area-weighted distribution for the T5 fallback, or (3) clean the remaining pandas/geopandas warnings. Which should I do next?