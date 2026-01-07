# Berlin Geo Heatmap

**Project Introduction**
- **Name**: Berlin Geo Heatmap (Project 1)
- **Purpose**: Visualize the heatmap for the amount of electric charging stations and residents. With this information a 3rd heatmap is being generated to show the demand defined by residents/charging station.

---

## Architecture Overview (DDD)

This project follows **Domain-Driven Design (DDD)** principles with a layered architecture:

```
+------------------+
|   Presentation   |  <- Streamlit UI, Map Components
+------------------+
        |
        v
+------------------+
|   Application    |  <- Services (thin orchestrators)
+------------------+
        |
        v
+------------------+
|     Domain       |  <- Entities, Value Objects, Events, Repository Interfaces
+------------------+
        ^
        |
+------------------+
|  Infrastructure  |  <- Repositories, Preprocessing, Utils
+------------------+
```

For detailed architecture diagrams, see `docs/`.

---

## Directory Organization

```
.
├── main.py                              # Composition Root (Entry Point)
├── config.py                            # Configuration (pdict)
├── README.md                            # This file
│
├── docs/                                # Architecture Documentation
│   ├── architecture/                    # DDD layer diagrams (draw.io)
│   └── domain/                          # Domain context diagrams
│
├── src/
│   ├── presentation/                    # UI Layer
│   │   ├── streamlit_app.py             # Main Streamlit app function
│   │   ├── components/                  # UI components (map, forms, lists)
│   │   └── utils/                       # Color maps, UI helpers
│   │
│   ├── shared/                          # Shared Bounded Context
│   │   ├── domain/
│   │   │   ├── value_objects/           # PostalCode
│   │   │   ├── events/                  # DomainEvent base class
│   │   │   ├── exceptions/              # DomainException, InvalidPostalCodeException
│   │   │   └── repositories/            # BaseRepository interface
│   │   ├── application/services/        # shared_service.py
│   │   └── infrastructure/
│   │       ├── preprocessing/           # stations.py, residents.py, geo_utils.py
│   │       ├── repositories/            # shared_repository.py
│   │       └── utils/                   # helper_tools.py (timer)
│   │
│   ├── demand/                          # Demand Bounded Context
│   │   ├── domain/
│   │   │   ├── entities/                # DemandResult (rich domain model)
│   │   │   ├── value_objects/           # DemandScore
│   │   │   ├── events/                  # DemandCalculatedEvent
│   │   │   ├── exceptions/              # InvalidDemandDataException
│   │   │   └── repositories/            # DemandRepositoryInterface
│   │   ├── application/services/        # demand_service.py
│   │   └── infrastructure/repositories/ # demand_repository.py, in_memory_...
│   │
│   └── suggestion/                      # Suggestion Bounded Context
│       ├── domain/
│       │   ├── entities/                # ChargingSuggestion (rich domain model)
│       │   ├── events/                  # SuggestionCreatedEvent, SuggestionReviewedEvent
│       │   ├── exceptions/              # InvalidSuggestionException
│       │   └── repositories/            # SuggestionRepositoryInterface
│       ├── application/services/        # suggestion_service.py
│       └── infrastructure/repositories/ # suggestion_repository.py, in_memory_...
│
├── tests/                               # Test Suite
│   ├── shared/                          # PostalCode tests
│   ├── demand/                          # Demand logic tests
│   ├── suggestions/                     # Suggestion persistence tests
│   ├── fakes/                           # Test doubles
│   └── test_smoke.py                    # Smoke tests for app verification
│
└── scripts/                             # Standalone scripts
    └── compute_demand.py                # Demand computation script
```

---

## What Each Module Does

### 1. `main.py` (Composition Root)
- Entry point for the Streamlit application
- Loads datasets using infrastructure repositories
- Calls preprocessing functions from `src/shared/infrastructure/preprocessing/`
- Invokes `make_streamlit_electric_charging_resid()` from presentation layer

### 2. Presentation Layer (`src/presentation/`)
- `streamlit_app.py`: Main UI function with tabs for Map, Suggestions, Reviews
- `components/map_view.py`: Renders Residents, Stations, Demand layers
- `components/suggestion_form.py`: User suggestion submission form
- `components/suggestion_list.py`: Admin review interface

### 3. Bounded Contexts

#### i. Shared Context (`src/shared/`)
*Foundation: Common components used across all contexts*

- **Value Objects**: `PostalCode` - Berlin PLZ validation (10000-14200)
- **Domain Events**: `DomainEvent` - Base class with event_id, timestamp
- **Exceptions**: `DomainException`, `InvalidPostalCodeException`
- **Repository Interface**: `BaseRepository` - Generic CRUD interface
- **Preprocessing**: `preprop_lstat()`, `preprop_resid()`, `sort_by_plz_add_geometry()`
- **Utils**: `timer` decorator for performance logging

#### ii. Demand Context (`src/demand/`)
*Brain: Calculates where new charging stations are needed*

- **Entity**: `DemandResult` - Rich domain model with:
  - `get_demand_category()` - Returns 'critical', 'high', 'medium', 'low', 'satisfied'
  - `is_high_demand()`, `is_medium_demand()` - Categorization methods
  - `get_priority_rank()` - Priority for infrastructure planning
- **Value Object**: `DemandScore` - Validates non-negative demand values
- **Domain Event**: `DemandCalculatedEvent` - Captures calculation results
- **Service**: `DemandService` - Thin orchestrator for calculation workflow

#### iii. Suggestion Context (`src/suggestion/`)
*Interaction: Manages user suggestions for new charging locations*

- **Entity**: `ChargingSuggestion` - Rich domain model with:
  - Status transitions: pending -> approved/rejected -> deleted
  - `approve()`, `reject()`, `delete()` - Business methods
  - `can_transition_to()` - Status validation
- **Domain Events**: `SuggestionCreatedEvent`, `SuggestionReviewedEvent`
- **Service**: `SuggestionService` - Thin orchestrator for CRUD operations

### 4. Testing (`tests/`)
- **TDD approach**: Red-Green-Refactor cycle
- **50 tests** covering:
  - Unit tests with `@pytest.mark.parametrize` for edge cases
  - Smoke tests for app-level verification
  - In-memory repositories for isolation

---

## Data Format & Column Requirements

### 1. Residents Data (`plz_einwohner.xlsx` - Sheet `T14`)

| Column Name | Format | Value Range | Notes |
|------------|--------|-------------|-------|
| `Postleitzahl` | Integer/String | 10001-14199 | Berlin postal codes |
| `Insgesamt` | Integer | 0-200,000+ | Total residents per PLZ |
| `Bezirk` (optional) | String | District names | Context information |

**Data Quality Notes:**
- 237 rows total, 190 unique PLZs
- Total sum: 3,902,645 residents
- Fallback to `T5` sheet if `T14` missing

### 2. Charging Stations (`Ladesaeulenregister.csv`)

| Column Name | Format | Value Range | Notes |
|------------|--------|-------------|-------|
| `Postleitzahl` | String/Integer | 10001-14199 | Join key |
| `Longitude` | Float | 13.08-13.76 | EPSG:4326 |
| `Latitude` | Float | 52.34-52.67 | EPSG:4326 |

**Data Quality Notes:**
- 3,657 valid stations in Berlin
- 3-4 metadata header rows (auto-detected)

### 3. PLZ Geometries (`geodata_berlin_plz.csv`)

| Column Name | Format | Notes |
|------------|--------|-------|
| `plz` | Integer/String | Join key |
| `geometry` | WKT String | POLYGON/MULTIPOLYGON |

### Expected Distributions

- **Residents per PLZ**: 5-200,000+; mean ~20,500
- **Stations per PLZ**: 0-60+; mean ~4-5
- **Demand (residents/stations)**: 0-28,386

---

## How to Run

**Start the Streamlit App:**
```bash
# With venv
.\.venv\Scripts\python.exe -m streamlit run .\main.py --server.port 8503

# Or after activating venv
streamlit run main.py --server.port 8503
```

**Run Tests:**
```bash
# All tests
python -m pytest

# Specific test suite
python -m pytest tests/demand/test_demand_logic.py

# Verbose output
python -m pytest -v
```

---

## Interpretation of Results

- **Residents layer**: Population density by PLZ
- **Charging Stations layer**: Station count per PLZ (yellow = 0 stations)
- **Demand layer**: Residents/stations ratio (red = high demand, priority for expansion)

**Top demand areas:**
| PLZ | Residents | Stations | Demand |
|-----|-----------|----------|--------|
| 12309 | 28,386 | 1 | 28,386 |
| 10247 | 41,630 | 2 | 20,815 |
| 13187 | 38,144 | 2 | 19,072 |

---

## Notes

- Data sources: Berlin statistics (T14, June 2025), Federal charging station registry
- Geometry: EPSG:4326 (WGS84)
- For area-proportional calculations, reproject to EPSG:25833

---

## Contact / Credits

**Team 6:**
- Muhammed Korkot
- Shoaib Ur Rehman Khan
- Chirayu Jain
- Montasir Hasan Chowdhury
