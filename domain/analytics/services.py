"""
Domain services for analytics.
"""
from typing import List, Dict, Optional
from datetime import datetime
import numpy as np

from .entities import DemandAnalysis, DemandMetrics, HeatmapData
from ..charging_infrastructure.repository import ChargingStationRepository
from ..demographics.repository import DemographicRepository


class AnalyticsService:
    """Domain service for analytics and demand calculations."""

    def __init__(self, charging_repo: ChargingStationRepository, demographic_repo: DemographicRepository):
        self.charging_repo = charging_repo
        self.demographic_repo = demographic_repo

    def calculate_demand_for_postal_code(self, postal_code: str) -> Optional[DemandAnalysis]:
        """Calculate charging demand for a specific postal code."""
        # Get data for this postal code
        station_count = self.charging_repo.count_by_postal_code(postal_code)
        resident_count = self.demographic_repo.get_population_by_postal_code(postal_code)

        if resident_count is None:
            return None

        # Calculate demand metrics
        if station_count > 0:
            residents_per_station = resident_count / station_count
        else:
            # No stations - high demand (use resident count as demand indicator)
            residents_per_station = float(resident_count)

        # Determine demand level
        demand_level = self._classify_demand_level(residents_per_station)

        metrics = DemandMetrics(
            residents_per_station=residents_per_station,
            demand_level=demand_level,
            station_count=station_count,
            resident_count=resident_count
        )

        return DemandAnalysis(
            postal_code=postal_code,
            metrics=metrics,
            calculated_at=datetime.now().isoformat()
        )

    def calculate_demand_for_all_areas(self) -> List[DemandAnalysis]:
        """Calculate demand for all postal areas."""
        analyses = []
        postal_codes = self.charging_repo.get_postal_codes_with_stations()

        for postal_code in postal_codes:
            analysis = self.calculate_demand_for_postal_code(postal_code)
            if analysis:
                analyses.append(analysis)

        return analyses

    def generate_heatmap_data(self, analyses: List[DemandAnalysis]) -> List[HeatmapData]:
        """Generate heatmap data from demand analyses."""
        if not analyses:
            return []

        # Extract demand scores
        demand_scores = [analysis.get_demand_score() for analysis in analyses]

        # Calculate percentiles for color scaling
        p95 = np.percentile(demand_scores, 95) if demand_scores else 1

        heatmap_data = []
        for analysis in analyses:
            score = analysis.get_demand_score()
            # Normalize color intensity (cap at 95th percentile)
            intensity = min(score / p95, 1.0) if p95 > 0 else 0.0

            heatmap_data.append(HeatmapData(
                postal_code=analysis.postal_code,
                value=score,
                color_intensity=intensity
            ))

        return heatmap_data

    def get_high_demand_areas(self, threshold: float = 50) -> List[str]:
        """Get postal codes with high charging demand."""
        analyses = self.calculate_demand_for_all_areas()
        return [analysis.postal_code for analysis in analyses
                if analysis.get_demand_score() > threshold]

    def _classify_demand_level(self, residents_per_station: float) -> str:
        """Classify demand level based on residents per station."""
        if residents_per_station >= 200:
            return "critical"
        elif residents_per_station >= 100:
            return "high"
        elif residents_per_station >= 50:
            return "medium"
        else:
            return "low"