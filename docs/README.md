# Architecture Documentation

This folder contains architecture documentation for the Berlin Electric Charging Stations Heatmap project.
Streamlit APP: https://heatmap-charging-stations-57gjuxh3nzacjdg3tdojua.streamlit.app/

## Current Architecture

The project follows a **Domain-Driven Design (DDD)** layered architecture with three bounded contexts.

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
|     Domain       |  <- Entities, Value Objects, Events, Exceptions
+------------------+
        ^
        |
+------------------+
|  Infrastructure  |  <- Repositories (JSON/Pandas), Preprocessing, Utils
+------------------+
```

---

## Source Code Structure

```
src/
├── presentation/                    # UI Layer (Streamlit)
│   ├── streamlit_app.py            # Main application
│   ├── components/
│   │   ├── map_view.py             # Map rendering
│   │   ├── suggestion_form.py      # User input form
│   │   └── suggestion_list.py      # Display suggestions
│   └── utils/
│       └── map_colors.py           # Color utilities
│
├── demand/                          # Demand Bounded Context
│   ├── application/services/
│   │   └── demand_service.py       # Demand calculation orchestrator
│   ├── domain/events/
│   │   ├── demand_calculated.py    # Calculate demand (function)
│   │   └── display_demand.py       # Render demand layer (function)
│   └── infrastructure/repositories/
│       ├── demand_repository.py    # File-based storage
│       └── in_memory_demand_repository.py  # For testing
│
├── suggestion/                      # Suggestion Bounded Context
│   ├── application/services/
│   │   └── suggestion_service.py   # Suggestion orchestrator
│   ├── domain/
│   │   ├── entities/
│   │   │   └── suggestion.py       # ChargingSuggestion (with State Machine)
│   │   └── exceptions/
│   │       └── invalid_suggestion_exception.py
│   └── infrastructure/repositories/
│       ├── suggestion_repository.py      # add(), get_all(), update()
│       └── in_memory_suggestion_repository.py  # For testing
│
└── shared/                          # Shared Bounded Context
    ├── application/services/
    │   └── shared_service.py       # Data loading orchestrator
    ├── domain/
    │   ├── value_objects/
    │   │   └── postal_code.py      # PostalCode Value Object
    │   ├── events/
    │   │   ├── residents_processed.py
    │   │   └── stations_processed.py
    │   └── exceptions/
    │       └── domain_exception.py  # Base exception class
    └── infrastructure/
        ├── preprocessing/
        │   ├── geo_utils.py        # Geographic utilities
        │   ├── stations.py         # Station data processing
        │   └── residents.py        # Resident data processing
        ├── repositories/
        │   └── shared_repository.py
        └── utils/
            └── helper_tools.py     # Timer decorator
```

---

## Bounded Contexts

### 1. Shared Context (`src/shared/`)

Common components used across all contexts:

- **Value Objects**: `PostalCode` - Validates Berlin postal codes (10000-14200)
- **Exceptions**: `DomainException` - Base class for domain errors
- **Events**: Data processing functions (residents, stations)
- **Infrastructure**: Preprocessing utilities, helper tools

### 2. Demand Context (`src/demand/`)

Handles demand calculation for charging stations:

- **Service**: `DemandService` - Orchestrates demand calculation
- **Events**: `on_demand_calculated()`, `display_demand()` - Core logic
- **Repository**: `DemandRepository` - Stores analysis results

### 3. Suggestion Context (`src/suggestion/`)

Manages user suggestions for new charging locations:

- **Entity**: `ChargingSuggestion` - Rich model with:
  - State Machine for status transitions (`pending` -> `approved`/`rejected` -> `deleted`)
  - Validation using `PostalCode` Value Object
  - Methods: `approve()`, `reject()`, `delete()`, `can_transition_to()`
- **Exception**: `InvalidSuggestionException` - For validation errors
- **Repository**: `SuggestionRepository` - Handles persistence:
  - `add()` - Assigns ID, timestamp, status='pending'
  - `get_visible_for_users()` - Returns pending + approved only (user view)
  - `get_all()` - Returns all except deleted (admin view)
  - `get_all_including_deleted()` - For review operations
  - `update()` - Saves changes after review
- **Service**: `SuggestionService` - Thin orchestrator between Entity and Repository:
  - `get_suggestions_for_users()` - User view (pending + approved)
  - `get_all_suggestions()` - Admin view (all except deleted)
  - `review_suggestion()` - Approve, reject, or delete

**User vs Admin Views:**
- **Users**: See only pending and approved suggestions (rejected hidden from public view)
- **Admins**: See all suggestions + can approve, reject, or delete any suggestion

---

## Key Design Decisions

### State Machine for Suggestions

The `ChargingSuggestion` entity enforces valid status transitions:

```python
VALID_STATUS_TRANSITIONS = {
    'pending': ['approved', 'rejected', 'deleted'],
    'approved': ['deleted'],
    'rejected': ['deleted'],
    'deleted': [],  # Terminal state
}
```

### PostalCode Value Object

Ensures all postal codes are valid Berlin PLZ:

```python
@dataclass(frozen=True)  # Immutable
class PostalCode:
    value: str

    def __post_init__(self):
        # Validates: 5 digits, range 10000-14200
```

### Dependency Injection

Services accept repositories via constructor, enabling testability:

```python
class SuggestionService:
    def __init__(self, repository):
        self._repository = repository  # Can be real or in-memory
```

---

## Test Structure

```
tests/
├── test_smoke.py                    # Import verification (10 tests)
├── shared/
│   └── test_postal_code.py          # Value Object tests (17 tests)
├── demand/
│   └── test_demand_logic.py         # Service tests (10 tests)
└── suggestion/
    └── test_suggestion_persistence.py  # Entity + State Machine tests (14 tests)
```

**Total: 51 tests**

---

