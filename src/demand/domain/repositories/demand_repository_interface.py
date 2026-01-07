"""
Repository Interface for Demand Results.

Defines the contract for demand data persistence operations,
following the Repository Pattern for dependency inversion.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any

from src.demand.domain.entities.demand_result import DemandResult


class DemandRepositoryInterface(ABC):
    """
    Abstract repository interface for demand calculation results.

    This interface defines operations for storing and retrieving
    demand analysis results. The demand data is typically calculated
    from residents and station counts, then stored for UI presentation.

    Implementing classes must provide concrete implementations for all methods.

    Example:
        >>> class PandasDemandRepository(DemandRepositoryInterface):
        ...     def store_results(self, results_df):
        ...         self._data = results_df
    """

    @abstractmethod
    def store_results(self, results_df: Any) -> None:
        """
        Store demand calculation results.

        Args:
            results_df: DataFrame or similar structure containing
                       demand results for all PLZ areas.
        """
        pass

    @abstractmethod
    def get_latest_results(self) -> Optional[Any]:
        """
        Retrieve the most recent demand calculation results.

        Returns:
            The stored results DataFrame, or None if no calculation
            has been performed yet.
        """
        pass

    @abstractmethod
    def get_by_plz(self, plz: str) -> Optional[DemandResult]:
        """
        Retrieve demand result for a specific postal code.

        Args:
            plz: The postal code to look up.

        Returns:
            DemandResult for the PLZ if found, None otherwise.
        """
        pass

    @abstractmethod
    def get_high_demand_areas(self, threshold: float = 10000.0) -> Any:
        """
        Retrieve all areas with demand above the threshold.

        Args:
            threshold: Minimum demand score to include. Default is 10000
                      (residents per station).

        Returns:
            DataFrame or list of high-demand areas.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear stored results.

        This is useful for resetting state between calculations.
        """
        pass
