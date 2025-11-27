**Project Introduction**
- **Name**: Berlin Geo Heatmap (Project 1)
- **Purpose**: Visualize the heatmap for the amount of electric charging stations and residents. With this information a 3rd heatmap is being generated to show the demand defined by residents/charging station.

**Directory Organization:**
- **Main app**: `main.py` — Streamlit app orchestrator that loads datasets, preprocesses them, and builds the interactive map.
- **Configuration**: `config.py` — small dictionary `pdict` with filenames and the geocode key (`PLZ`).
- **Core code**: `berlingeoheatmap_project1\core\methods.py` — preprocessing and map-building functions.
- **Helpers**: `berlingeoheatmap_project1\core\HelperTools.py` — timing and small utilities.
- **Scripts**: `scripts\compute_demand.py` — standalone script to compute demand metrics and generate summary reports.
- **Datasets folder**: `berlingeoheatmap_project1\datasets`
  - PLZ polygons: `geodata_berlin_plz.csv` (WKT geometry)
  - Charging stations registry: `Ladesaeulenregister.csv` (original registry with metadata header lines)
  - Residents: `plz_einwohner.xlsx` (sheet `T14` is preferred for per-PLZ counts, this has been added manually because there was no csv for this given. Also this dataset is more up to date) https://www.statistik-berlin-brandenburg.de/a-i-5-hj
  - Bezirke shapefiles: `datasets\berlin_bezirke\bezirksgrenzen.shp` (used for T5 fallback mapping, contains residents per district)

**What Each Module Does:**

1. **`main.py`** (Streamlit Orchestrator)
   - Loads all datasets using functions from `core.methods`
   - Preprocesses residents, charging stations, and geometry data
   - Detects which visualization layer user selects (Residents / Charging_Stations / Demand) via Streamlit radio button
   - Calls `make_streamlit_electric_Charging_resid()` to generate the interactive folium map
   - Displays map and data statistics in Streamlit UI
   - Timing and diagnostics via `HelperTools.py`

2. **`config.py`** (Configuration)
   - Defines `pdict` dictionary with key file paths and column names:
     - `'geodata_plz_file'`: path to `geodata_berlin_plz.csv`
     - `'charging_stations_file'`: path to `Ladesaeulenregister.csv`
     - `'residents_file'`: path to `plz_einwohner.xlsx`
     - `'bezirke_file'`: path to shapefile for fallback
     - `'geocode_key'`: column name used for grouping (`PLZ`)

3. **`core/methods.py`** (Data Processing & Visualization)
   - **`sort_by_plz_add_geometry()`**: Loads PLZ polygons from `geodata_berlin_plz.csv`, parses WKT geometries, computes centroids
   - **`preprop_resid()`**: Reads `plz_einwohner.xlsx` sheet `T14`, detects header rows, aggregates residents by PLZ
   - **`preprop_lstat()`**: Reads `Ladesaeulenregister.csv` with metadata header detection, filters for valid charging stations, assigns to PLZs via geocoding
   - **`make_streamlit_electric_Charging_resid()`**: Main visualization function that:
     - Merges residents, charging stations, and demand data into full PLZ geometry set
     - Creates color scales (linear for Residents/Charging_Stations, 95th-percentile capped for Demand)
     - Builds three interactive folium layers with popups showing PLZ, district, count, and demand ratio
     - Returns folium map object for display in Streamlit

4. **`core/HelperTools.py`** (Utilities)
   - `get_current_time()`: Timing and execution logging
   - Simple utilities for consistent formatting

5. **`scripts/compute_demand.py`** (Standalone Demand Computation)
   - Reads residents from `T14` and charging stations from registry
   - Computes demand metric (residents / stations per PLZ)
   - Generates `tmp_plz_demand.csv` (all PLZs ranked by demand)
   - Generates `tmp_plz_demand_summary.json` (summary statistics: mean, median, 95th percentile, top PLZs)
   - Run independently with: `python scripts/compute_demand.py`

---

## **Data Format & Column Requirements**

### **1. Residents Data (`plz_einwohner.xlsx` — Sheet `T14`)**

| Column Name | Format | Value Range | Plausible Values | Notes |
|------------|--------|-------------|-----------------|-------|
| `Postleitzahl` | Integer or String | 10001–14199 | 10247, 12309, 13187, etc. | 5-digit Berlin postal codes; used as join key with PLZ geometries |
| `Insgesamt` | Integer (whole numbers) | 0–200,000+ | 28,386 (PLZ 12309), 41,630 (PLZ 10247) | Total residents in that PLZ within that district; summed across all rows = 3,902,645 |
| `Bezirk` (optional) | String | District names | Mitte, Charlottenburg-Wilmersdorf, etc. | Helps identify which district residents belong to; kept for context |

**Data Quality Notes for T14:**
- **Structure**: 237 rows total, 190 unique PLZs (some PLZs appear in multiple rows/districts)
- **Distribution**: Highly skewed; central districts (Mitte, Friedrichshain-Kreuzberg) have higher concentrations
- **Aggregation**: Each row represents a unique (PLZ, district) combination; summing all `Insgesamt` values = 3,902,645 (verified correct)
- **Fallback (T5)**: If `T14` sheet is missing, code falls back to `T5` (Bezirke/district-level data) and distributes residents to PLZs proportionally by area

### **2. Charging Stations Registry (`Ladesaeulenregister.csv`)**

| Column Name | Format | Value Range | Plausible Values | Notes |
|------------|--------|-------------|-----------------|-------|
| `Postleitzahl` | String or Integer | 10001–14199 | 10247, 12309, 13187, etc. | 5-digit Berlin postal code; primary join key with PLZ geometries and residents |
| `Longitude` | Float | 13.08–13.76 | 13.4050, 13.2195, etc. | Geographic coordinates (EPSG:4326, WGS84); used for fallback geocoding if PLZ missing |
| `Latitude` | Float | 52.34–52.67 | 52.5200, 52.4500, etc. | Geographic coordinates (EPSG:4326, WGS84); used for fallback geocoding if PLZ missing |
| `Betreiber` | String | Text (company names) | Vattenfall, Shell, Aral, etc. | Operator/company name; kept for metadata, not used in heatmap computation |
| Other columns (optional) | String/Integer | Various | `Inbetriebnahme`, `Ladetyp`, etc. | Additional metadata (date, charging type, etc.); ignored in computation |

**Data Quality Notes for Ladesaeulenregister:**
- **File structure**: Contains 3–4 metadata/header rows at top (automatically detected and skipped by `preprop_lstat()`)
- **Total stations**: 3,657 valid rows counted in Berlin datasets
- **Distribution**: Highly concentrated in central districts (Mitte, Charlottenburg-Wilmersdorf); sparse in outer districts (Treptow-Köpenick, Spandau)
- **Fallback geocoding**: If `Postleitzahl` missing, code reverse-geocodes using `Latitude`/`Longitude` to find nearest PLZ via centroid-distance matching
- **Duplicates**: Some charging stations listed multiple times (e.g., different connectors, different operators); current logic counts them individually per row

### **3. PLZ Geometries (`geodata_berlin_plz.csv`)**

| Column Name | Format | Value Range | Plausible Values | Notes |
|------------|--------|-------------|-----------------|-------|
| `plz` | Integer or String | 10001–14199 | 10247, 12309, 13187, etc. | 5-digit postal code; primary join key for merging with residents & stations |
| `geometry` | WKT String | POLYGON or MULTIPOLYGON | `POLYGON((13.08 52.34, 13.09 52.34, ...))` | Well-Known Text format; parsed into shapely Polygon/MultiPolygon objects by geopandas |

**Data Quality Notes for geodata_berlin_plz.csv:**
- **CRS**: Geographic (EPSG:4326, WGS84) — uses lat/lon coordinates
- **Completeness**: Contains all 190 unique Berlin PLZs; ensures every PLZ boundary is visually displayed
- **Geometry validity**: All WKT strings are valid polygons (no self-intersections, no empty/null geometries)
- **Centroid computation**: Code automatically computes polygon centroids for label placement and reference

### **Expected Distributions & Value Ranges:**

- **Residents per PLZ**: Range 5–200,000+; most common 10,000–50,000; mean ~20,500; total sum 3,902,645
- **Charging stations per PLZ**: Range 0–60+; most common 0–5 stations; mean ~4–5 (3,657 total / ~190 unique PLZs); distribution is highly left-skewed with outliers
- **Demand (residents / stations)**: Range 0–28,386 (when stations = 1); median ~3,000–5,000; 95th percentile ~10,000 (color scale cap to avoid outlier saturation)
- **Latitude/Longitude**: Latitude 52.34–52.67 (north-south extent of Berlin); Longitude 13.08–13.76 (east-west extent); all in EPSG:4326

---

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

**Notes**
- Data quality: Residents are from official Berlin statistics (T14, updated June 2025); charging stations from federal registry (Ladesaeulenregister).
- Geometry: PLZ polygons are in geographic CRS (EPSG:4326). For precise area-proportional calculations, reproject to a projected CRS (e.g., EPSG:25833).
- Warning suppression: Some pandas/geopandas warnings (SettingWithCopyWarning, CRS warnings) can be cleaned by specifying dtypes and using `.loc` assignments. See code comments for details.

**Contact / Credits**

Team 6:
- Shoaib Ur Rehman Khan
- Chirayu Jain
- Muhammed Korkot
- Montasir Hasan Chowdhury 