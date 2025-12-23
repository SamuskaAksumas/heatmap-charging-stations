"""
Infrastructure repository implementations.
"""
import os
import pandas as pd
import geopandas as gpd
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain.charging_infrastructure.entities import ChargingStation, Location, Capacity
from domain.charging_infrastructure.repository import ChargingStationRepository
from domain.geography.entities import PostalArea, Coordinate
from domain.geography.repository import PostalAreaRepository
from domain.demographics.entities import DemographicArea, PopulationData
from domain.demographics.repository import DemographicRepository
from domain.community_engagement.entities import ChargingSuggestion, SuggestionStatus, ReviewInfo
from domain.community_engagement.repository import SuggestionRepository


class CsvChargingStationRepository(ChargingStationRepository):
    """CSV-based implementation of charging station repository."""

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self._stations: Optional[List[ChargingStation]] = None

    def _load_data(self) -> List[ChargingStation]:
        """Load charging station data from CSV."""
        if self._stations is not None:
            return self._stations

        # Read CSV with proper encoding and header row (row 10 contains headers)
        df = pd.read_csv(self.csv_path, sep=';', header=10, encoding='iso-8859-1', low_memory=False)

        # Filter for Berlin postal codes (Berlin PLZ range: 10000-14200)
        df = df[df['Postleitzahl'].astype(str).str.match(r'^1[0-4]\d{3}$', na=False)]

        stations = []
        for _, row in df.iterrows():
            try:
                # Parse coordinates (handle German decimal format)
                lat_str = str(row['Breitengrad']).replace(',', '.')
                lon_str = str(row['Längengrad']).replace(',', '.')
                
                location = Location(
                    latitude=float(lat_str),
                    longitude=float(lon_str)
                )
                
                # Parse power capacity
                power_kw = float(row['Nennleistung Ladeeinrichtung [kW]']) if pd.notna(row['Nennleistung Ladeeinrichtung [kW]']) else 0.0
                
                capacity = Capacity(
                    power_kw=power_kw,
                    connector_type=row.get('Steckertypen1', 'Unknown')
                )
                
                # Create address from street and house number
                address_parts = []
                if pd.notna(row.get('Straße')):
                    address_parts.append(str(row['Straße']))
                if pd.notna(row.get('Hausnummer')):
                    address_parts.append(str(row['Hausnummer']))
                address = ', '.join(address_parts) if address_parts else None
                
                station = ChargingStation(
                    station_id=str(row['Ladeeinrichtungs-ID']),
                    location=location,
                    capacity=capacity,
                    postal_code=str(row['Postleitzahl']),
                    address=address,
                    operator=str(row['Betreiber']) if pd.notna(row['Betreiber']) else None
                )
                
                stations.append(station)
                
            except (ValueError, KeyError, TypeError) as e:
                # Skip invalid rows
                continue

        self._stations = stations
        return stations

    def get_all(self) -> List[ChargingStation]:
        return self._load_data()

    def get_by_postal_code(self, postal_code: str) -> List[ChargingStation]:
        return [s for s in self._load_data() if s.postal_code == postal_code]

    def get_by_id(self, station_id: str) -> Optional[ChargingStation]:
        return next((s for s in self._load_data() if s.station_id == station_id), None)

    def count_by_postal_code(self, postal_code: str) -> int:
        return len(self.get_by_postal_code(postal_code))

    def get_postal_codes_with_stations(self) -> List[str]:
        postal_codes = set(s.postal_code for s in self._load_data())
        return sorted(list(postal_codes))


class ShapefilePostalAreaRepository(PostalAreaRepository):
    """Shapefile-based implementation of postal area repository."""

    def __init__(self, shapefile_path: str, population_data: Optional[Dict[str, int]] = None):
        self.shapefile_path = shapefile_path
        self.population_data = population_data or {}
        self._areas: Optional[List[PostalArea]] = None
        self._gdf: Optional[gpd.GeoDataFrame] = None

    def _load_data(self) -> List[PostalArea]:
        """Load postal area data from shapefile."""
        if self._areas is not None:
            return self._areas

        # Load shapefile
        gdf = gpd.read_file(self.shapefile_path)
        self._gdf = gdf

        areas = []
        for _, row in gdf.iterrows():
            try:
                postal_code = str(row['PLZ']).strip()
                population = self.population_data.get(postal_code)

                # Calculate centroid
                centroid = row['geometry'].centroid
                centroid_coord = Coordinate(latitude=centroid.y, longitude=centroid.x)

                area = PostalArea(
                    postal_code=postal_code,
                    geometry=row['geometry'],
                    centroid=centroid_coord,
                    population=population
                )
                areas.append(area)
            except (ValueError, KeyError):
                continue

        self._areas = areas
        return areas

    def get_all(self) -> List[PostalArea]:
        return self._load_data()

    def get_by_postal_code(self, postal_code: str) -> Optional[PostalArea]:
        try:
            for area in self._load_data():
                if area.postal_code == postal_code:
                    return area
            print(f"[DEBUG] No PostalArea found for PLZ {postal_code} in shapefile.")
            return None
        except Exception as e:
            print(f"[EXCEPTION] Error in get_by_postal_code for PLZ {postal_code}: {e}")
            return None

    def get_postal_codes_in_range(self, min_code: str, max_code: str) -> List[PostalArea]:
        areas = self._load_data()
        return [area for area in areas
                if min_code <= area.postal_code <= max_code]

    def find_postal_area_for_coordinate(self, coordinate: Coordinate) -> Optional[PostalArea]:
        areas = self._load_data()
        for area in areas:
            if area.contains_point(coordinate):
                return area
        return None

    def get_centroid_for_postal_code(self, postal_code: str) -> Optional[Coordinate]:
        try:
            area = self.get_by_postal_code(postal_code)
            if area and area.centroid:
                return area.centroid
            print(f"[DEBUG] No centroid for PLZ {postal_code} (area found: {bool(area)}).")
            return None
        except Exception as e:
            print(f"[EXCEPTION] Error in get_centroid_for_postal_code for PLZ {postal_code}: {e}")
            return None

    def get_geodataframe(self) -> gpd.GeoDataFrame:
        if self._gdf is None:
            self._load_data()
        return self._gdf.copy()


class ExcelDemographicRepository(DemographicRepository):
    """Excel-based implementation of demographic repository."""

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self._areas: Optional[List[DemographicArea]] = None

    def _load_data(self) -> List[DemographicArea]:
        """Load demographic data from Excel."""
        if self._areas is not None:
            return self._areas

        # For now, create mock demographic data for Berlin postal codes
        # since the Excel file doesn't contain the expected population data
        berlin_postal_codes = [
            '10115', '10117', '10119', '10178', '10179', '10243', '10245', '10247', '10249',
            '10315', '10317', '10318', '10319', '10365', '10367', '10369', '10405', '10407',
            '10409', '10435', '10437', '10439', '10551', '10553', '10555', '10557', '10559',
            '10585', '10587', '10589', '10623', '10625', '10627', '10629', '10707', '10709',
            '10711', '10713', '10715', '10717', '10719', '10777', '10779', '10781', '10783',
            '10785', '10787', '10789', '10823', '10825', '10827', '10829', '10961', '10963',
            '10965', '10967', '10969', '10997', '10999', '12043', '12045', '12047', '12049',
            '12051', '12053', '12055', '12057', '12059', '12099', '12101', '12103', '12105',
            '12107', '12109', '12157', '12159', '12161', '12163', '12165', '12167', '12169',
            '12203', '12205', '12207', '12209', '12247', '12249', '12277', '12279', '12305',
            '12307', '12309', '12347', '12349', '12351', '12353', '12355', '12357', '12359',
            '12435', '12437', '12439', '12459', '12487', '12489', '12524', '12526', '12527',
            '12555', '12557', '12559', '12587', '12589', '12619', '12621', '12623', '12627',
            '12629', '12679', '12681', '12683', '12685', '12687', '12689', '13051', '13053',
            '13055', '13057', '13059', '13086', '13088', '13089', '13125', '13127', '13129',
            '13156', '13158', '13159', '13187', '13189', '13347', '13349', '13351', '13353',
            '13355', '13357', '13359', '13403', '13405', '13407', '13409', '13435', '13437',
            '13439', '13465', '13467', '13469', '13503', '13505', '13507', '13509', '13581',
            '13583', '13585', '13587', '13589', '13591', '13593', '13595', '13597', '13599',
            '13627', '13629', '13739', '14050', '14052', '14053', '14055', '14057', '14059',
            '14089', '14109', '14129', '14131', '14163', '14165', '14167', '14169', '14193',
            '14195', '14197', '14199'
        ]

        areas = []
        for postal_code in berlin_postal_codes:
            # Mock population data - using a base population with some variation
            base_population = 5000 + (int(postal_code) % 1000) * 10
            pop_data = PopulationData(total_population=base_population)
            area = DemographicArea(
                postal_code=postal_code,
                population_data=pop_data
            )
            areas.append(area)

        self._areas = areas
        return areas

    def get_all(self) -> List[DemographicArea]:
        return self._load_data()

    def get_by_postal_code(self, postal_code: str) -> Optional[DemographicArea]:
        return next((area for area in self._load_data() if area.postal_code == postal_code), None)

    def get_population_by_postal_code(self, postal_code: str) -> Optional[int]:
        area = self.get_by_postal_code(postal_code)
        return area.population if area else None

    def get_total_population(self) -> int:
        return sum(area.population for area in self._load_data())

    def get_postal_codes_by_population_range(self, min_pop: int, max_pop: int) -> List[str]:
        areas = self._load_data()
        return [area.postal_code for area in areas
                if min_pop <= area.population <= max_pop]


class JsonSuggestionRepository(SuggestionRepository):
    """JSON-based implementation of suggestion repository."""

    def __init__(self, json_path: str):
        self.json_path = json_path

    def _ensure_file_exists(self):
        """Ensure the JSON file exists."""
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w', encoding='utf-8') as f:
                f.write('[]')

    def save(self, suggestion: ChargingSuggestion) -> None:
        suggestions = self.get_all()
        suggestions.append(suggestion)
        self._save_all(suggestions)

    def get_all(self) -> List[ChargingSuggestion]:
        self._ensure_file_exists()
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = pd.read_json(f)
                if data.empty:
                    return []

                suggestions = []
                for _, row in data.iterrows():
                    # Parse status
                    status_str = row.get('status', 'pending')
                    status = SuggestionStatus(status_str)

                    # Parse review info
                    review_info = None
                    if pd.notna(row.get('reviewed_by')):
                        review_info = ReviewInfo(
                            reviewer=row['reviewed_by'],
                            review_date=datetime.fromisoformat(row['review_date']),
                            notes=row.get('review_notes')
                        )

                    suggestion = ChargingSuggestion(
                        id=int(row['id']),
                        postal_code=str(row['plz']),
                        address=str(row['address']),
                        reason=str(row['reason']),
                        submitted_at=datetime.fromisoformat(row['timestamp']),
                        status=status,
                        review_info=review_info
                    )
                    suggestions.append(suggestion)

                return suggestions
        except (FileNotFoundError, ValueError, KeyError):
            return []

    def get_by_id(self, suggestion_id: int) -> Optional[ChargingSuggestion]:
        suggestions = self.get_all()
        return next((s for s in suggestions if s.id == suggestion_id), None)

    def get_by_postal_code(self, postal_code: str) -> List[ChargingSuggestion]:
        suggestions = self.get_all()
        return [s for s in suggestions if s.postal_code == postal_code]

    def get_by_status(self, status: SuggestionStatus) -> List[ChargingSuggestion]:
        suggestions = self.get_all()
        return [s for s in suggestions if s.status == status]

    def update(self, suggestion: ChargingSuggestion) -> None:
        suggestions = self.get_all()
        for i, s in enumerate(suggestions):
            if s.id == suggestion.id:
                suggestions[i] = suggestion
                break
        self._save_all(suggestions)

    def get_pending_suggestions(self) -> List[ChargingSuggestion]:
        return self.get_by_status(SuggestionStatus.PENDING)

    def get_approved_suggestions(self) -> List[ChargingSuggestion]:
        return self.get_by_status(SuggestionStatus.APPROVED)

    def _save_all(self, suggestions: List[ChargingSuggestion]) -> None:
        """Save all suggestions to JSON file."""
        data = []
        for suggestion in suggestions:
            item = {
                'id': suggestion.id,
                'plz': suggestion.postal_code,
                'address': suggestion.address,
                'reason': suggestion.reason,
                'timestamp': suggestion.submitted_at.isoformat(),
                'status': suggestion.status.value
            }

            if suggestion.review_info:
                item.update({
                    'reviewed_by': suggestion.review_info.reviewer,
                    'review_date': suggestion.review_info.review_date.isoformat(),
                    'review_notes': suggestion.review_info.notes
                })

            data.append(item)

        with open(self.json_path, 'w', encoding='utf-8') as f:
            pd.DataFrame(data).to_json(f, orient='records', indent=2, force_ascii=False)