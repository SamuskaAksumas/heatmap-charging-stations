# Berlin Charging Station Map - DDD Architecture

This project implements a Domain-Driven Design (DDD) architecture for visualizing Berlin's charging infrastructure and analyzing demand for electric vehicle charging stations.

## Architecture Overview

The application follows DDD principles with clear separation of concerns across four layers:

### Domain Layer (`domain/`)
Contains the core business logic and domain entities:

- **charging_infrastructure/**: Charging station entities and business rules
- **geography/**: Geographic entities and postal area management
- **demographics/**: Population data and demographic analysis
- **community_engagement/**: User suggestions and community features
- **analytics/**: Demand analysis and heatmap generation

### Application Layer (`application/`)
Contains use case implementations and application services:

- **services/**: Application services that orchestrate domain services for specific use cases

### Infrastructure Layer (`infrastructure/`)
Handles external concerns and data persistence:

- **repositories/**: Concrete implementations of repository interfaces for data access

### Presentation Layer (`presentation/`)
User interface components:

- **ui.py**: Streamlit-based web interface

## Key Features

- **Interactive Map**: Visualize charging stations and demand heatmaps
- **Demand Analysis**: Identify areas needing additional charging infrastructure
- **Community Suggestions**: Allow users to suggest new charging locations
- **Analytics Dashboard**: Comprehensive metrics and insights

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure data files are in place:
- `datasets/geodata_berlin_dis.csv` (charging station data)
- `datasets/berlin_postleitzahlen/berlin_postleitzahlen.shp` (postal area boundaries)
- `datasets/demographics.xlsx` (population data - to be created)

## Usage

### Running the Application
```bash
python main_ddd.py
```

### Running Tests
```bash
python -m pytest tests/
```

## Domain Entities

### Charging Infrastructure
- `ChargingStation`: Represents an EV charging station
- `Location`: Geographic coordinates (latitude/longitude)
- `Capacity`: Charging capacity and connector type

### Geography
- `PostalArea`: Berlin postal code areas with geometric boundaries
- `Coordinate`: Geographic coordinate value object

### Community Engagement
- `ChargingSuggestion`: User-submitted location suggestions
- `SuggestionStatus`: Enum for suggestion states (pending/approved/rejected)
- `ReviewInfo`: Review metadata for approved/rejected suggestions

### Analytics
- `DemandAnalysis`: Analysis results for postal code areas
- `DemandMetrics`: Calculated demand metrics
- `HeatmapData`: Data points for visualization

## Bounded Contexts

1. **ChargingInfrastructure**: Manages charging station data and capacity
2. **Geography**: Handles Berlin postal areas and spatial operations
3. **Demographics**: Population data and demographic analysis
4. **CommunityEngagement**: User suggestions and community features
5. **Analytics**: Demand analysis and visualization data

## Configuration

Application settings are defined in `config_ddd.py`:
- Data file paths
- Berlin geographic boundaries
- Analytics thresholds
- UI settings

## Development

### Adding New Features
1. Define domain entities in the appropriate bounded context
2. Create repository interfaces in the domain layer
3. Implement concrete repositories in the infrastructure layer
4. Add application services for use cases
5. Update the presentation layer UI

### Testing
- Domain logic is tested with unit tests in `tests/test_domain.py`
- Use pytest for running tests
- Mock external dependencies for isolated testing

## Data Sources

- **Charging Stations**: CSV file with station locations and capacities
- **Postal Areas**: Shapefile with Berlin postal code boundaries
- **Demographics**: Excel file with population statistics (to be implemented)
- **Suggestions**: JSON file for storing user suggestions

## Dependencies

- **pandas/geopandas**: Data processing and geospatial operations
- **streamlit**: Web interface
- **folium**: Interactive maps
- **pytest**: Unit testing
- **shapely**: Geometric operations