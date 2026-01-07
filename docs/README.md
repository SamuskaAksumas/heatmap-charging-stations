# Architecture Documentation

This folder contains architecture diagrams for the Berlin Electric Charging Stations Heatmap project.

## Diagram Overview

### Architecture Diagrams (`architecture/`)

1. **ddd-layers.drawio** - DDD Layer Architecture
   - Shows the 4 layers: Presentation, Application, Domain, Infrastructure
   - Dependencies flow: Presentation -> Application -> Domain <- Infrastructure

2. **bounded-contexts.drawio** - Bounded Contexts Overview
   - Shows the 3 bounded contexts: Shared, Demand, Suggestion
   - Shows their relationships and shared components

3. **component-diagram.drawio** - Component Dependencies
   - Shows how components interact across layers

### Domain Diagrams (`domain/`)

1. **demand-context.drawio** - Demand Bounded Context
   - DemandResult Entity
   - DemandScore Value Object
   - DemandCalculatedEvent
   - DemandRepositoryInterface

2. **suggestion-context.drawio** - Suggestion Bounded Context
   - ChargingSuggestion Entity
   - SuggestionCreatedEvent, SuggestionReviewedEvent
   - SuggestionRepositoryInterface

---

## DDD Architecture Overview

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
|  Infrastructure  |  <- Repositories (JSON/Pandas), Preprocessing, Utils
+------------------+
```

## Bounded Contexts

### 1. Shared Context (`src/shared/`)
Common components used across all contexts:
- **Value Objects**: PostalCode
- **Domain Events**: DomainEvent (base class)
- **Exceptions**: DomainException, InvalidPostalCodeException
- **Repository Interface**: BaseRepository
- **Infrastructure**: Preprocessing (stations, residents, geo_utils), Utils (timer)

### 2. Demand Context (`src/demand/`)
Handles demand calculation for charging stations:
- **Entity**: DemandResult (rich domain model with categorization)
- **Value Object**: DemandScore
- **Domain Event**: DemandCalculatedEvent
- **Exception**: InvalidDemandDataException
- **Service**: DemandService (thin orchestrator)
- **Repository**: DemandRepository, InMemoryDemandRepository

### 3. Suggestion Context (`src/suggestion/`)
Handles user suggestions for new charging locations:
- **Entity**: ChargingSuggestion (rich domain model with status transitions)
- **Domain Events**: SuggestionCreatedEvent, SuggestionReviewedEvent
- **Exception**: InvalidSuggestionException
- **Service**: SuggestionService (thin orchestrator)
- **Repository**: SuggestionRepository, InMemorySuggestionRepository

---

## Key Design Decisions

### Rich Domain Models
Entities contain business logic, not just data:
- `ChargingSuggestion.approve()`, `.reject()`, `.can_transition_to()`
- `DemandResult.get_demand_category()`, `.is_high_demand()`

### Repository Pattern
- Domain layer defines interfaces (`SuggestionRepositoryInterface`)
- Infrastructure implements them (`SuggestionRepository`)
- Enables dependency inversion and testing

### Domain Events
- Immutable records of domain occurrences
- Support event-driven architecture
- Base class: `DomainEvent` with `event_id`, `timestamp`

### Value Objects
- Immutable, self-validating
- `PostalCode`: Berlin PLZ validation (10000-14200)
- `DemandScore`: Non-negative demand value
