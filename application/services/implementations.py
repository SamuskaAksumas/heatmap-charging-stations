"""
Application services for use cases.
"""
from typing import List, Dict, Optional
import pandas as pd

from domain.charging_infrastructure.services import ChargingStationService
from domain.geography.services import GeographyService
from domain.analytics.services import AnalyticsService
from domain.demographics.services import DemographicsService
from domain.community_engagement.entities import ChargingSuggestion, SuggestionStatus
from domain.community_engagement.repository import SuggestionRepository
from domain.analytics.entities import DemandAnalysis, HeatmapData


class MapService:
    """Application service for map-related use cases."""

    def __init__(self, charging_service: ChargingStationService,
                 geography_service: GeographyService,
                 analytics_service: AnalyticsService,
                 demographics_service: DemographicsService):
        self.charging_service = charging_service
        self.geography_service = geography_service
        self.analytics_service = analytics_service
        self.demographics_service = demographics_service

    def generate_residents_layer(self) -> Dict[str, int]:
        """Generate data for residents visualization layer."""
        # Get all demographic areas and return population by postal code
        residents_data = {}
        demographic_areas = self.demographics_service.get_all_demographic_areas()
        for area in demographic_areas:
            residents_data[area.postal_code] = area.population
        return residents_data

    def generate_charging_stations_layer(self) -> Dict[str, int]:
        """Generate data for charging stations visualization layer."""
        return self.charging_service.get_stations_summary_by_postal_code()

    def generate_demand_layer(self) -> List[DemandAnalysis]:
        """Generate data for demand visualization layer."""
        return self.analytics_service.calculate_demand_for_all_areas()

    def get_heatmap_data(self) -> List[HeatmapData]:
        """Get heatmap data for visualization."""
        demand_analyses = self.generate_demand_layer()
        return self.analytics_service.generate_heatmap_data(demand_analyses)


class SuggestionService:
    """Application service for suggestion management use cases."""

    def __init__(self, suggestion_repo: SuggestionRepository, geography_service: GeographyService):
        self.suggestion_repo = suggestion_repo
        self.geography_service = geography_service

    def submit_suggestion(self, postal_code: str, address: str, reason: str) -> ChargingSuggestion:
        """Submit a new charging location suggestion."""
        if not self.geography_service.validate_berlin_postal_code(postal_code):
            raise ValueError("Invalid Berlin postal code")

        # Generate new ID
        all_suggestions = self.suggestion_repo.get_all()
        new_id = max([s.id for s in all_suggestions], default=0) + 1

        suggestion = ChargingSuggestion(
            id=new_id,
            postal_code=postal_code,
            address=address,
            reason=reason,
            submitted_at=pd.Timestamp.now().to_pydatetime()
        )

        self.suggestion_repo.save(suggestion)
        return suggestion

    def review_suggestion(self, suggestion_id: int, action: str, reviewer: str, notes: str = "") -> bool:
        """Review a suggestion (approve/reject)."""
        suggestion = self.suggestion_repo.get_by_id(suggestion_id)
        if not suggestion:
            return False

        if action.lower() == 'approve':
            suggestion.approve(reviewer, notes)
        elif action.lower() == 'reject':
            suggestion.reject(reviewer, notes)
        else:
            return False

        self.suggestion_repo.update(suggestion)
        return True

    def get_suggestions_by_postal_code(self, postal_code: str) -> List[ChargingSuggestion]:
        """Get all suggestions for a postal code."""
        return self.suggestion_repo.get_by_postal_code(postal_code)

    def get_pending_suggestions(self) -> List[ChargingSuggestion]:
        """Get all pending suggestions for review."""
        return self.suggestion_repo.get_pending_suggestions()

    def get_approved_suggestions(self) -> List[ChargingSuggestion]:
        """Get all approved suggestions."""
        return self.suggestion_repo.get_approved_suggestions()


class AnalyticsServiceApp:
    """Application service for analytics use cases."""

    def __init__(self, analytics_service: AnalyticsService):
        self.analytics_service = analytics_service

    def get_demand_analysis(self, postal_code: str) -> Optional[DemandAnalysis]:
        """Get demand analysis for a specific postal code."""
        return self.analytics_service.calculate_demand_for_postal_code(postal_code)

    def get_high_demand_areas(self, threshold: float = 50) -> List[str]:
        """Get postal codes with high charging demand."""
        return self.analytics_service.get_high_demand_areas(threshold)

    def generate_demand_report(self) -> Dict:
        """Generate a comprehensive demand report."""
        analyses = self.analytics_service.calculate_demand_for_all_areas()

        report = {
            'total_areas_analyzed': len(analyses),
            'high_demand_areas': len([a for a in analyses if a.is_high_demand()]),
            'areas_needing_stations': len([a for a in analyses if a.needs_more_stations()]),
            'average_demand_score': sum(a.get_demand_score() for a in analyses) / len(analyses) if analyses else 0
        }

        return report